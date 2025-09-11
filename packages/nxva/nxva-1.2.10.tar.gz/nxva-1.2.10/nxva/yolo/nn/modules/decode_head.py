from tarfile import XGLTYPE
import numpy as np
import torch
import torch.nn as nn

def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

def _softmax(x, axis):
    x = x - np.max(x, axis=axis, keepdims=True)
    ex = np.exp(x)
    return ex / np.sum(ex, axis=axis, keepdims=True)

def _make_anchorsV5(feats, na, anchors, strides, grid_cell_offset=-0.5):
    """use NumPy to generate anchors."""
    grids, anchor_grids, strides_grids = [], [], []
    for i, stride in enumerate(strides):
        *_, h, w = feats[i].shape
        # create grid coordinates
        sx = np.arange(w, dtype=np.float32) + grid_cell_offset
        sy = np.arange(h, dtype=np.float32) + grid_cell_offset
        sy, sx = np.meshgrid(sy, sx, indexing="ij")  # shape: (h, w)

        # stack coordinate points
        points = np.stack((sx, sy), axis=-1).reshape(1, 1, -1, 2)  # shape: (h * w, 2)
        points = np.repeat(points, na, axis=1).reshape(1, -1, 2)
        grids.append(points)

        # make anchor grids
        anchor = anchors[i]
        anchor = anchor.reshape(1, na, 1, 1, 2) + np.zeros((1,1,h,w,1), dtype=anchors.dtype)
        anchor = anchor.reshape(1, -1, 2)
        anchor_grids.append(anchor)

        # make stride grids
        strides = np.full((1, na * h * w, 1), stride, dtype=np.float32)
        strides_grids.append(strides)
    return np.concatenate(grids, axis=1), np.concatenate(anchor_grids, axis=1), np.concatenate(strides_grids, axis=1)

def _transform_feat(feat, na, no):
    x_feats = []
    B = feat[0].shape[0]
    for i, xi in enumerate(feat):
        *_, H, W = xi.shape
        xi = xi.reshape(B, na, no, H, W).transpose(0, 1, 3, 4, 2).reshape(B, -1, no)  # (B,na,H,W,no) => B, -1, no
        x_feats.append(xi)  # (B,na*H*W,no)
    return np.concatenate(x_feats, axis=1)  # (B, sum(na*H*W), no)



class DecodeDetectV11:
    def __init__(self, nc=80, reg_max=16):
        self.reg_max = reg_max
        self.no = nc + reg_max*4

        self.strides = np.array([8., 16., 32.])
        self.anchors_grid, self.strides_grid = None, None

    def forward(self, x):
        for i in x:
            print(i.shape, 'x')
        B = x[0].shape[0]

        #1. cat aligned feature maps
        print(self.no, 'self.no')
        x_cat = np.concatenate([xi.reshape(B, self.no, -1) for xi in x], axis=2)
        print(x_cat.shape, 'x_cat')

        #2. make anchors and strides
        if self.anchors_grid is None or self.strides_grid is None:
            self.anchors_grid, self.strides_grid = self._make_anchors(x, self.strides, grid_cell_offset=0.5)

        print(self.anchors_grid.shape, 'self.anchors_grid')
        print(self.strides_grid.shape, 'self.strides_grid')
        #3. split x_cat into box and cls
        box, cls = np.split(x_cat, [self.reg_max * 4], axis=1)
        print('='*20)
        print(box.shape, 'box')
        print(cls.shape, 'cls')
        print('='*20)

        #4. dfl
        box = self.dfl(box)
        cls = _sigmoid(cls)
        print(box.shape, 'box')
        print(cls.shape, 'cls')
        print('='*20)
        # #5. decode bbox
        dbox = self.decode_bboxes(box, self.anchors_grid) * self.strides_grid
        print(dbox.shape, 'dbox')
        print(cls.shape, 'cls')
        print('='*20)
        return np.concatenate([dbox, cls], axis=1)

    def _make_anchors(self, feats, strides, grid_cell_offset=0.5):
        """use NumPy to generate anchors."""
        anchor_points, stride_tensor = [], []

        assert feats is not None
        for i, stride in enumerate(strides):
            if isinstance(feats, list):
                h, w = feats[i].shape[2:]  # (B, C, H, W)
            else:
                h, w = int(feats[i][0]), int(feats[i][1])

            # create grid coordinates
            sx = np.arange(w, dtype=np.float32) + grid_cell_offset
            sy = np.arange(h, dtype=np.float32) + grid_cell_offset
            sy, sx = np.meshgrid(sy, sx, indexing="ij")  # shape: (h, w)

            # stack coordinate points
            points = np.stack((sx, sy), axis=-1).reshape(-1, 2)  # shape: (h * w, 2)
            anchor_points.append(points)

            # each anchor assigned a stride value
            stride_arr = np.full((h * w, 1), stride, dtype=np.float32)
            stride_tensor.append(stride_arr)

        return np.concatenate(anchor_points, axis=0).reshape(1, 2, -1), np.concatenate(stride_tensor, axis=0).reshape(1, 1, -1)

    def dfl(self, feat):
        b, _, fn = feat.shape #batch size, feature channel and feature number
        bins = np.arange(self.reg_max).reshape(1, 1, self.reg_max, 1)
        bins = np.broadcast_to(bins, (b, 4, self.reg_max, fn))
        feat = feat.reshape(b, 4, self.reg_max, fn)
        feat = _softmax(feat, axis=2)
        ltrb = (feat * bins).sum(axis=2) 
        return ltrb
    
    def decode_bboxes(self, box, anchors):
        return self._dist2bbox(box, anchors, dim=1)

    def _dist2bbox(self, distance, anchor_points, dim=1):
        """Transform distance(ltrb) to box(xywh or xyxy)."""
        lt, rb = np.split(distance, 2, axis=dim)
        x1y1 = anchor_points - lt
        x2y2 = anchor_points + rb
        c_xy = (x1y1 + x2y2) / 2
        wh = x2y2 - x1y1
        return np.concatenate((c_xy, wh), dim)  # xywh bbox


class DecodePoseV11(DecodeDetectV11):
    def __init__(self, nc=1, kpt_shape=(17, 3)):
        super().__init__(nc=nc)
        self.nc = nc
        self.kpt_shape = kpt_shape
        self.nk = kpt_shape[0] * kpt_shape[1]
        self.anchor_grid, self.strides_grid = None, None
    
    def forward(self, x):
        bbox_heads, kpt_heads = x
        B = bbox_heads[0].shape[0]
        x_cat = np.concatenate([xi.reshape(B, self.nk, -1) for xi in kpt_heads], axis=-1)

        bbox = DecodeDetectV11.forward(self, bbox_heads)

        pred_kpt = self.decode_kpts(x_cat)
        return np.concatenate((bbox, pred_kpt), axis=1)
    
    def decode_kpts(self, kpts):
        return self._dist2bbox(kpts)
    
    def _dist2bbox(self, kpts):
        ndim = self.kpt_shape[1]
        kpts[:, 2::ndim] = _sigmoid(kpts[:, 2::ndim])
        kpts[:, 0::ndim] = (kpts[:, 0::ndim] * 2.0 + (self.anchors_grid[:, 0, :] - 0.5)) * self.strides_grid
        kpts[:, 1::ndim] = (kpts[:, 1::ndim] * 2.0 + (self.anchors_grid[:, 1, :] - 0.5)) * self.strides_grid
        return kpts


class DecodeDetectV5:
    anchors = np.array([
        [[10, 13],  [16, 30],  [33, 23]],
        [[30, 61],  [62, 45],  [59, 119]],
        [[116, 90], [156, 198], [373, 326]]
    ], dtype=np.float32)
    strides = np.array([8., 16., 32.])
    
    def __init__(self, nc=80):
        self.na = len(self.anchors[0])
        self.no = nc + 5
        self.anchor_grid, self.strides_grid = None, None

    def forward(self, x):
        #1. cat aligned feature maps
        x_cat = _transform_feat(x, self.na, self.no)
        
        #2. make anchors and strides
        if self.anchor_grid is None or self.strides_grid is None:
            self.grid, self.anchor_grid, self.strides_grid = _make_anchorsV5(x, self.na, self.anchors, self.strides, grid_cell_offset=-0.5)

        #3. split x_cat into box and cls
        xy, wh, conf = np.split(_sigmoid(x_cat), [2, 4], axis=2)

        # #4. decode bbox
        return self.decode_bboxes(xy, wh, conf)

    def decode_bboxes(self, xy, wh, conf):
        return self._dist2bbox(xy, wh, conf)
    
    def _dist2bbox(self, xy, wh, conf):
        """Transform xy(ltrb) to box(xywh or xyxy)."""
        xy = (xy * 2 + self.grid) * self.strides_grid
        wh = (wh * 2) ** 2 * self.anchor_grid
        return np.concatenate((xy, wh, conf), axis=-1)


class DecodePoseV5:
    def __init__(self, nc=1, kpt_shape=(17, 3)):
        self.strides = np.array([8., 16., 32., 64.])
        self.anchors = np.array([
               [[ 19.,  27.],
                [ 44.,  40.],
                [ 38.,  94.]],

               [[ 96.,  68.],
                [ 86., 152.],
                [180., 137.]],

               [[140., 301.],
                [303., 264.],
                [238., 542.]],

               [[436., 615.],
                [739., 380.],
                [925., 792.]]])

        self.nc = 1
        self.no = nc + 5
        self.na = len(self.anchors[0])
        self.kpt_shape = kpt_shape
        self.nk = kpt_shape[0] * kpt_shape[1]
        self.anchor_grid, self.strides_grid = None, None

    def forward(self, x):
        bbox_heads, kpt_heads = x[:4], x[4:]
        #concat bbox and kpt feat

        # bbox_x0 = np.load('./yolov5_pose_heads_input/bbox_x0.npy')
        # bbox_x1 = np.load('./yolov5_pose_heads_input/bbox_x1.npy')
        # bbox_x2 = np.load('./yolov5_pose_heads_input/bbox_x2.npy')
        # bbox_x3 = np.load('./yolov5_pose_heads_input/bbox_x3.npy')

        # kpts_x0 = np.load('./yolov5_pose_heads_input/kpt_x0.npy')
        # kpts_x1 = np.load('./yolov5_pose_heads_input/kpt_x1.npy')
        # kpts_x2 = np.load('./yolov5_pose_heads_input/kpt_x2.npy')
        # kpts_x3 = np.load('./yolov5_pose_heads_input/kpt_x3.npy')

        # kpt_heads = [kpts_x0, kpts_x1, kpts_x2, kpts_x3]
        # bbox_heads = [bbox_x0, bbox_x1, bbox_x2, bbox_x3]

        kpts = _transform_feat(kpt_heads, self.na, self.nk)
        boxes = _transform_feat(bbox_heads, self.na, self.no)

        # make grid and anchor
        if self.anchor_grid is None or self.strides_grid is None:
            self.grid, self.anchor_grid, self.strides_grid = _make_anchorsV5(bbox_heads, self.na, self.anchors, self.strides, grid_cell_offset=-0.5)

        xy, wh, conf = np.split(_sigmoid(boxes), [2, 4], axis=-1)
        pred_boxes = self.decode_bboxes(xy, wh, conf)

        pred_kpt = self.decode_kpts(_sigmoid(kpts))
        return np.concatenate([pred_boxes, pred_kpt], axis=-1)
    
    def decode_kpts(self, kpts):
        return self._dist2kpts(kpts)

    def decode_bboxes(self, xy, wh, conf):
        return self._dist2bbox(xy, wh, conf)
    
    def _dist2bbox(self, xy, wh, conf):
        xy = (xy * 2 + self.grid) * self.strides_grid
        wh = (wh * 2) ** 2 * self.anchor_grid
        return np.concatenate((xy, wh, conf), axis=-1)
    
    def _dist2kpts(self, kpts):
        x = kpts[:, :, 0::3]
        y = kpts[:, :, 1::3]
        conf = kpts[:, :, 2::3]

        x = (x * 2.0 + (self.grid[:, :, 0:1])) * self.strides_grid
        y = (y * 2.0 + (self.grid[:, :, 1:2])) * self.strides_grid
        conf = _sigmoid(conf)
        return np.concatenate((x, y, conf), axis=-1)

# class DecodePoseV5(nn.Module):
#     stride = None  # strides computed during build
#     export = False  # onnx export

#     def __init__(self, nc=80, anchors=(), nkpt=None, ch=(), inplace=True, dw_conv_kpt=False):  # detection layer
#         self.nc = nc  # number of classes
#         self.nkpt = nkpt
#         self.dw_conv_kpt = dw_conv_kpt
#         self.no_det=(nc + 5)  # number of outputs per anchor for box and class
#         self.no_kpt = 3*self.nkpt ## number of outputs per anchor for keypoints
#         self.no = self.no_det+self.no_kpt
#         self.nl = len(anchors)  # number of detection layers
#         self.na = len(anchors[0]) // 2  # number of anchors
#         self.grid = [torch.zeros(1)] * self.nl  # init grid
#         self.flip_test = False
#         a = torch.tensor(anchors).float().view(self.nl, -1, 2)
#         self.register_buffer('anchors', a)  # shape(nl,na,2)
#         self.register_buffer('anchor_grid', a.clone().view(self.nl, 1, -1, 1, 1, 2))  # shape(nl,1,na,1,1,2)
#         self.m = nn.ModuleList(nn.Conv2d(x, self.no_det * self.na, 1) for x in ch)  # output conv
#         if self.nkpt is not None:
#             if self.dw_conv_kpt: #keypoint head is slightly more complex
#                 self.m_kpt = nn.ModuleList(
#                             nn.Sequential(DWConv(x, x, k=3), Conv(x,x),
#                                           DWConv(x, x, k=3), Conv(x, x),
#                                           DWConv(x, x, k=3), Conv(x,x),
#                                           DWConv(x, x, k=3), Conv(x, x),
#                                           DWConv(x, x, k=3), Conv(x, x),
#                                           DWConv(x, x, k=3), nn.Conv2d(x, self.no_kpt * self.na, 1)) for x in ch)
#             else: #keypoint head is a single convolution
#                 self.m_kpt = nn.ModuleList(nn.Conv2d(x, self.no_kpt * self.na, 1) for x in ch)

#         self.inplace = inplace  # use in-place ops (e.g. slice assignment)

#     def forward(self, x):
#         # x = x.copy()  # for profiling
        
#         z = []  # inference output
#         self.training |= self.export
#         for i in range(self.nl):
#             if self.nkpt is None or self.nkpt==0:
#                 x[i] = self.m[i](x[i])
#             else :
#                 x[i] = torch.cat((self.m[i](x[i]), self.m_kpt[i](x[i])), axis=1) #1x18x40x40

#             bs, _, ny, nx = x[i].shape  
#             x[i] = x[i].view(bs, self.na, self.no, ny, nx).permute(0, 1, 3, 4, 2).contiguous()
#             x_det = x[i][..., :6]
#             x_kpt = x[i][..., 6:]
#             np.save(f'../npu_exp/yolov5_pose_heads_torch/x_kpt{i}.npy', x_kpt.cpu().numpy())
#             np.save(f'../npu_exp/yolov5_pose_heads_torch/x_det{i}.npy', x_det.cpu().numpy())

#             if not self.training:  # inference
#                 if self.grid[i].shape[2:4] != x[i].shape[2:4]:
#                     self.grid[i] = self._make_grid(nx, ny).to(x[i].device)
#                 kpt_grid_x = self.grid[i][..., 0:1]
#                 kpt_grid_y = self.grid[i][..., 1:2]
#                 self.grid[i] = self.grid[i].to(x[i].device)
#                 self.stride[i] = self.stride[i].to(x[i].device)
#                 self.anchor_grid[i] = self.anchor_grid[i].to(x[i].device)
#                 kpt_grid_x = kpt_grid_x.to(x[i].device)
#                 kpt_grid_y = kpt_grid_y.to(x[i].device)

#                 if self.nkpt == 0:
#                     y = x[i].sigmoid()
#                 else:
#                     y = x_det.sigmoid()

#                 if self.inplace:
#                     print(self.grid[i], 'self.grid[i]')
#                     xy = (y[..., 0:2] * 2. - 0.5 + self.grid[i]) * self.stride[i]  # xy
#                     wh = (y[..., 2:4] * 2) ** 2 * self.anchor_grid[i].view(1, self.na, 1, 1, 2) # wh
#                     if self.nkpt != 0:
#                         x_kpt[..., 0::3] = (x_kpt[..., ::3] * 2. - 0.5 + kpt_grid_x.repeat(1,1,1,1,17)) * self.stride[i]  # xy
#                         x_kpt[..., 1::3] = (x_kpt[..., 1::3] * 2. - 0.5 + kpt_grid_y.repeat(1,1,1,1,17)) * self.stride[i]  # xy
#                         x_kpt[..., 2::3] = x_kpt[..., 2::3].sigmoid()
#                     y = torch.cat((xy, wh, y[..., 4:], x_kpt), dim = -1)
#                 z.append(y.view(bs, -1, self.no))
#         return (torch.cat(z, 1), x)

# class DecodePoseV5:
#     def __init__(self, nc=1, kpt_shape=(17, 3)):
#         self.strides = np.array([8., 16., 32., 64.])
#         self.anchors = np.array([
#                [[ 19.,  27.],
#                 [ 44.,  40.],
#                 [ 38.,  94.]],

#                [[ 96.,  68.],
#                 [ 86., 152.],
#                 [180., 137.]],

#                [[140., 301.],
#                 [303., 264.],
#                 [238., 542.]],

#                [[436., 615.],
#                 [739., 380.],
#                 [925., 792.]]])
#         self.nc = 1
#         self.nl = len(self.anchors)
#         self.boxes_no = nc + 5
#         self.kpts_no = kpt_shape[0] * kpt_shape[1]
#         self.no = self.boxes_no + self.kpts_no
#         self.na = len(self.anchors[0])
#         self.grid = [None] * self.nl

#     def forward(self, x):
#         bbox_heads, kpt_heads = x[:4], x[4:]
#         x = []
#         for i in range(self.nl):
#             bs, _, ny, nx = bbox_heads[i].shape
#             bbox_heads[i] = bbox_heads[i].reshape(bs, self.na, self.boxes_no, ny, nx).transpose(0, 1, 3, 4, 2)
#             kpt_heads[i] = kpt_heads[i].reshape(bs, self.na, self.kpts_no, ny, nx).transpose(0, 1, 3, 4, 2)
#             x_det = bbox_heads[i]
#             x_kpt = kpt_heads[i]
#             if self.grid[i] is None or self.grid[i].shape[2:4] != (ny, nx):
#                 self.grid[i] = self._make_grid(nx, ny)
#                 print(self.grid[i], 'self.grid[i]')
#             y = _sigmoid(x_det)
#             xy = (y[..., 0:2] * 2. + self.grid[i]) * self.strides[i]
#             wh = (y[..., 2:4] * 2) ** 2 * self.anchors[i].reshape(1, self.na, 1, 1, 2)
#             kpt_grid_x = self.grid[i][..., 0:1]
#             kpt_grid_y = self.grid[i][..., 1:2]
#             x_kpt[..., 0::3] = (x_kpt[..., 0::3] * 2.0 + np.repeat(kpt_grid_x, 17, axis=-1)) * self.strides[i]
#             x_kpt[..., 1::3] = (x_kpt[..., 1::3] * 2.0 + np.repeat(kpt_grid_y, 17, axis=-1)) * self.strides[i]
#             x_kpt[..., 2::3] = _sigmoid(x_kpt[..., 2::3])
#             y = np.concatenate((xy, wh, y[..., 4:], x_kpt), axis=-1)
#             x.append(y.reshape(bs, -1, self.no))
#         return np.concatenate(x, axis=1)

#     def _make_grid(self, nx=20, ny=20):
#         """Generates a mesh grid for anchor boxes with optional compatibility for torch versions < 1.10."""
#         shape = 1, self.na, ny, nx, 2  # grid shape
#         y, x = np.arange(ny), np.arange(nx)
#         yv, xv = np.meshgrid(y, x)  # torch>=0.7 compatibility
#         return np.broadcast_to(np.stack((yv, xv), 2).reshape(1, 1, ny, nx, 2), shape) - 0.5

# class DecodePoseV5(nn.Module):
#     stride = None  # strides computed during build
#     export = False  # onnx export

#     def __init__(self, nc=80, anchors=(), kpt_shape=(17, 3)):  # detection layer
#         self.nc = nc  # number of classes
#         nkpt = kpt_shape[0] * kpt_shape[1]
#         self.nkpt = nkpt
#         self.no_det=(nc + 5)  # number of outputs per anchor for box and class
#         self.no_kpt = self.nkpt ## number of outputs per anchor for keypoints
#         self.no = self.no_det+self.no_kpt
#         self.nl = 4  # number of detection layers
#         self.na = 3  # number of anchors
#         self.grid = [torch.zeros(1)] * self.nl  # init grid
#         self.flip_test = False
#         self.strides = np.array([8., 16., 32., 64.])
#         self.anchors = np.array([
#             [[ 19.,  27.],
#                 [ 44.,  40.],
#                 [ 38.,  94.]],

#             [[ 96.,  68.],
#                 [ 86., 152.],
#                 [180., 137.]],

#             [[140., 301.],
#                 [303., 264.],
#                 [238., 542.]],

#             [[436., 615.],
#                 [739., 380.],
#                 [925., 792.]]])

#         self.anchor_grid = torch.tensor(self.anchors).float()
#         self.strides = torch.tensor(self.strides).float()

#         self.inplace = False  # use in-place ops (e.g. slice assignment)

#     def forward(self, x):
#         self.anchor_grid = self.anchor_grid.view(self.nl, 1, -1, 1, 1, 2)
#         bbox_heads, kpt_heads = x[:4], x[4:]
#         for i in bbox_heads:
#             print(i.shape, 'bbox_heads[i].shape')
#         for i in kpt_heads:
#             print(i.shape, 'kpt_heads[i].shape')
#         print(self.no_det, 'self.no_det')
#         print(self.no_kpt, 'self.no_kpt')

#         for i, b in enumerate(bbox_heads):
#             B, C, H, W = b.shape
#             print(b.shape, 'b.shape')
#             bbox_heads[i] = torch.from_numpy(bbox_heads[i]).view(B, self.na, self.no_det, H, W).permute(0, 1, 3, 4, 2).contiguous()
#             print(bbox_heads[i].shape, 'bbox_heads[i].shape')

#         for i, k in enumerate(kpt_heads):
#             B, C, H, W = k.shape
#             kpt_heads[i] = torch.from_numpy(kpt_heads[i]).view(B, self.na, self.no_kpt, H, W).permute(0, 1, 3, 4, 2).contiguous()
#             print(kpt_heads[i].shape, 'kpt_heads[i].shape')
        


#         z = []  # inference output
#         for i in range(self.nl):
#             bs, _, ny, nx = x[i].shape  # x(bs,255,20,20) to x(bs,3,20,20,85)
#             x_det = bbox_heads[i]
#             x_kpt = kpt_heads[i]

#             if self.grid[i].shape[2:4] != x[i].shape[2:4]:
#                 self.grid[i] = self._make_grid(nx, ny)
#             kpt_grid_x = self.grid[i][..., 0:1]
#             kpt_grid_y = self.grid[i][..., 1:2]

#             if self.nkpt == 0:
#                 y = x[i].sigmoid()
#             else:
#                 y = x_det.sigmoid()

#             # print('='*20)
#             # print(y.shape, 'y.shape')
#             # print(self.grid[i].shape, 'self.grid[i].shape')
#             # print(self.strides[i].shape, 'self.strides[i].shape')
#             # print(self.anchor_grid[i].shape, 'self.anchor_grid[i].shape')
#             # print(y[..., 0:2].shape, 'y[..., 0:2].shape')
#             # print(y[..., 2:4].shape, 'y[..., 2:4].shape')
#             # print('='*20)
#             xy = (y[..., 0:2] * 2. - 0.5 + self.grid[i]) * self.strides[i]  # xy
#             wh = (y[..., 2:4] * 2) ** 2 * self.anchor_grid[i].view(1, self.na, 1, 1, 2) # wh
#             x_kpt[..., 0::3] = (x_kpt[..., ::3] * 2. - 0.5 + kpt_grid_x.repeat(1,1,1,1,17)) * self.strides[i]  # xy
#             x_kpt[..., 1::3] = (x_kpt[..., 1::3] * 2. - 0.5 + kpt_grid_y.repeat(1,1,1,1,17)) * self.strides[i]  # xy
#             x_kpt[..., 2::3] = x_kpt[..., 2::3].sigmoid()
#             y = torch.cat((xy, wh, y[..., 4:], x_kpt), dim = -1)
#             z.append(y.view(bs, -1, 57))
#         return (torch.cat(z, 1), x)

#     @staticmethod
#     def _make_grid(nx=20, ny=20):
#         yv, xv = torch.meshgrid([torch.arange(ny), torch.arange(nx)])
#         return torch.stack((xv, yv), 2).view((1, 1, ny, nx, 2)).float()


class DecodeSegmentV5(DecodeDetectV5):
    def __init__(self, nc=80):
        super().__init__(nc=nc)

    def forward(self, x):
        segment_feat, detect_feat = x
        x = DecodeDetectV5.forward(self, detect_feat)
        return (x[0], segment_feat)


class DecodeSegmentV11(DecodeDetectV11):
    def __init__(self, nc=80):
        super().__init__(nc=nc)
    
    def forward(self, x):
        segment_feat, detect_feat, mask_coeffs = x
        x = DecodeDetectV11.forward(self, detect_feat)
        return (np.concatenate((x[0], mask_coeffs), axis=1), segment_feat)


class DecodeClassify:
    def __init__(self):
        pass
    
    def forward(self, x):
        return _sigmoid(x, axis=1)

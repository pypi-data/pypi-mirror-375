"""
AutoBackend Class - Automatic Backend Model Loader

This class provides a unified interface to automatically load YOLO models in different formats.
It supports multiple model formats (PyTorch, ONNX, TensorRT Engine, TorchScript) and task types
(detection, segmentation, pose estimation, classification).

Main Features:
- Automatically selects appropriate backend handler based on model file extension
- Supports multiple YOLO task types
- Provides unified model loading and inference interface
- Automatically handles model loading for different devices (CPU/GPU)
"""

from typing import Union, List, Optional
from pathlib import Path
import logging


LOGGER = logging.getLogger(__name__)


class AutoBackend:
    _REGISTER = {}
    def __init__(self, model_path: str, device: str, config: dict):
        """
        Initialize the automatic backend loader
        
        Args:
            model_path (str): Path to the model file
            device (str): Computing device (e.g., 'cpu', 'cuda:0')
            config (dict): Configuration dictionary, must contain 'task' and 'version' keys
        
        Raises:
            ValueError: Raised when task type is not supported or model format is not supported
        """
        self.model_path = model_path
        self.config = config
        self.device = device
        self.model = self.load_model()  # Load the model during initialization

    def __init_subclass__(cls, *, exts: str, **kwargs):
        super().__init_subclass__(**kwargs)
        for ext in exts:
            cls._REGISTER[ext.lower()] = cls

    def __new__(cls, model_path, *args):
        if cls is AutoBackend:  # 只有當你是從 AutoBackend 建立時才分派
            suffix = Path(model_path).suffix.lower()  # → ".pt"
            real_cls = cls._REGISTER[suffix]              # → TorchHandler
            return super().__new__(real_cls)          # 建立 TorchHandler 實體
        return super().__new__(cls)                   # 如果是子類自己被呼叫，就照常建立

    def __call__(self, imgs):
        """
        Execute model inference
        
        This is an abstract method that subclasses must implement to perform actual inference.
        
        Args:
            imgs: Input images, format determined by specific implementation
            
        Returns:
            Inference results, format determined by specific implementation
            
        Raises:
            NotImplementedError: Raised when subclass does not implement this method
        """
        raise NotImplementedError("Subclasses should overwrite this method to run the detection!")
        
    def load_model(self):
        """
        Load the model
        
        This is an abstract method that subclasses must implement to load models of corresponding format.
        
        Returns:
            Loaded model object
            
        Raises:
            NotImplementedError: Raised when subclass does not implement this method
        """
        raise NotImplementedError("Subclasses should overwrite this method to load the model!")

        
class EngineHandler(AutoBackend, exts=['.engine']):
    def __init__(self, model_path, device, config: dict):
        super().__init__(model_path, device, config)
        
    def __call__(self, imgs):
        return self.model.infer([imgs])

    def load_model(self):
        from nxva.nxtrt import TRTInference        
        self.size = self.config['size']
        return TRTInference(self.config['weights'],  [(1, 3, self.size, self.size)])

    
class TorchHandler(AutoBackend, exts=['.pt', '.pth']):
    def __init__(self, model_path, device, config: dict):
        super().__init__(model_path, device, config)      

    def __call__(self, imgs):
        import torch
        imgs = torch.from_numpy(imgs)
        imgs = imgs.to(self.device)
        with torch.no_grad():
            pred = self.model(imgs)
        return pred

    def load_model(self):
        import torch
        from ..utils.torch_utils import attempt_load
        if self.device.split(':')[0] == 'cuda' and not torch.cuda.is_available():
            LOGGER.warning("CUDA is not available, using CPU")
            self.device = 'cpu'

        replace = self.replace_module(self.config)
        model = attempt_load(self.config['weights'], device=self.device, replace=replace, task=self.config['task'], version=self.config['version'])
        model = model.half().eval() if self.config['fp16'] else model.float().eval()
        return model

    def replace_module(self, config: dict):
        # just for .pt
        version = config['version'].lower()
        task = config['task']
        if version == 'yolov5':
            if task == 'pose':
                config['replace'] = {'Detect': 'PoseV5', 'Model': 'PoseModel', 'Upsample': 'torch1_10_Upsample'}
            elif task == 'detect':
                config['replace'] = {'Detect': 'DetectV5', 'Model': 'DetectionModel', 'Upsample': 'torch1_10_Upsample'}
            elif task == 'segment':
                config['replace'] = {'Segment': 'SegmentV5', 'Detect': 'DetectV5'}
            elif task == 'classify':
                config['replace'] = {'Classify': 'ClassifyV5'}
        elif version in ['yolov5u', 'yolov8', 'yolo11']: 
            if task == 'pose':
                config['replace'] = {'Pose': 'PoseV11', 'Detect': 'DetectV11'}
            elif task == 'detect':
                config['replace'] = {'Detect': 'DetectV11'}
            elif task == 'segment':
                config['replace'] = {'Segment': 'SegmentV11', 'Detect': 'DetectV11'}
            elif task == 'classify':
                config['replace'] = {'Classify': 'ClassifyV11'}
        else:
            raise ValueError(f"Unsupported version: {version}. Supported versions: {self.supported_versions}")
        return config['replace']


class OnnxHandler(AutoBackend, exts=['.onnx']):
    def __init__(self, model_path, device, config: dict):
        super().__init__(model_path, device, config)        

    def __call__(self, imgs):
        pred = self.model.run(None, {self.model.get_inputs()[0].name: imgs})
        # add decode head to test NPU .onnx work or not
        # pred = self.decoder_cls.forward(pred)
        return pred


    def load_model(self):
        import onnxruntime as ort
        if self.device.split(':')[0] == 'cuda':
            if ort.get_available_providers() == ['CPUExecutionProvider']:
                LOGGER.warning("CUDA is not available, using CPU")
                providers = ["CPUExecutionProvider"]
                return ort.InferenceSession(self.config['weights'], providers=providers)
            else:
                device_id = self.device.split(':')[1]
                if device_id is None:
                    device_id = 0
                providers = [("CUDAExecutionProvider", {"device_id": device_id})]
                return ort.InferenceSession(self.config['weights'], providers=providers)
        elif self.device == 'cpu':
            providers = ["CPUExecutionProvider"]
            return ort.InferenceSession(self.config['weights'], providers=providers)
        else:
            raise ValueError(f"Unsupported provider: {self.device}")

        
class JitHandler(AutoBackend, exts=['.jit']):
    def __init__(self, model_path, device, config: dict):
        super().__init__(model_path, device, config)

    def __call__(self, imgs):
        import torch
        with torch.no_grad():
            pred = self.model(imgs)[0]
        return pred

    def load_model(self):
        import torch
        if self.device.split(':')[0] == 'cuda' and not torch.cuda.is_available():
            LOGGER.warning("CUDA is not available, using CPU")
            self.device = 'cpu'

        model = torch.jit.load(self.config['weights'], map_location=self.device)
        model = model.half().eval() if self.fp16 else model.float().eval()
        return model


class NefHandler(AutoBackend, exts=['.nef']):
    dev_dict = {} #port_id : dev
    def __init__(self, model_path, device, config:dict):
        super().__init__(model_path, device, config)
        from nxva.nxkp import decode_yolo_head

        self.size = self.config['size']
        self.version = self.config['version']
        self.task = self.config['task'] 
        self.model_id = self.config['model_id']
        self.decode_yolo_head = decode_yolo_head

    def __call__(self, imgs):
        results = []
        for img in imgs:
            results.append(self.decode_yolo_head(self.model.infer(img, model_id=self.model_id), img_size=(self.size, self.size), version=self.version, task=self.task))
        return results
    
    def load_model(self):
        from nxva.nxkp import KneronDevice, InferenceSession, scan_devices
        #parse device
        usb_port_id = self.config.get('usb_port_id', None)
        device_config = self.device.split(':')
        _, platform, *rest = device_config
        device_id = int(rest[0]) if rest else None

        if usb_port_id is not None:
            pass
        elif device_id is not None:
            platform_id = int('100' if platform == '520' else platform, 16)
            scan_results = [d.usb_port_id for d in scan_devices() if d.product_id == platform_id]

            if device_id >= len(scan_results):
                raise ValueError(f"device id not found in device: {device_id}")
            
            usb_port_id = scan_results[device_id]
        else:
            raise ValueError(f"usb port id or device id not found")
            
        if usb_port_id in self.dev_dict:
            dev = self.dev_dict[usb_port_id]
        else:
            dev = KneronDevice(platform=platform)
            dev.usb_port_id = usb_port_id
            dev.connect()
            self.dev_dict[usb_port_id] = dev

        session = InferenceSession(
            device=dev,
            nef_path=self.config['weights'],
            version = self.config['version'],
            task = self.config['task'],
            max_inflight = 1
        )
        return session
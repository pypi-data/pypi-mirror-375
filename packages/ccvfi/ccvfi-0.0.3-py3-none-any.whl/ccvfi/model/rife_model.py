from typing import Any, List

import cv2
import numpy as np
import torch
from torchvision import transforms

from ccvfi.arch import IFNet
from ccvfi.model import MODEL_REGISTRY
from ccvfi.model.vfi_base_model import VFIBaseModel
from ccvfi.type import ModelType
from ccvfi.util.misc import de_resize, resize


@MODEL_REGISTRY.register(name=ModelType.RIFE)
class RIFEModel(VFIBaseModel):
    def load_model(self) -> Any:
        state_dict = self.get_state_dict()

        model = IFNet()

        def _convert(param: Any) -> Any:
            return {k.replace("module.", ""): v for k, v in param.items() if "module." in k}

        model.load_state_dict(_convert(state_dict), strict=False)
        model.eval().to(self.device)
        return model

    @torch.inference_mode()  # type: ignore
    def inference(self, imgs: torch.Tensor, timestep: float, scale: float) -> torch.Tensor:
        """
        Inference with the model

        :param imgs: The input frames (B, 2, C, H, W)
        :param timestep: Timestep between 0 and 1 (img0 and img1)
        :param scale: Flow scale.

        :return: an immediate frame between I0 and I1
        """

        I0, I1 = imgs[:, 0], imgs[:, 1]
        _, _, h, w = I0.shape
        I0 = resize(I0, scale)
        I1 = resize(I1, scale)

        inp = torch.cat([I0, I1], dim=1)
        scale_list = [16 / scale, 8 / scale, 4 / scale, 2 / scale, 1 / scale]

        result = self.model(inp, timestep, scale_list)

        result = de_resize(result, h, w)

        return result

    @torch.inference_mode()  # type: ignore
    def inference_image_list(self, img_list: List[np.ndarray]) -> List[np.ndarray]:
        """
        Inference numpy image list with the model

        :param img_list: 2 input frames (img0, img1)

        :return: 1 output frames (img0_1)
        """
        if len(img_list) != 2:
            raise ValueError("IFNet img_list must contain 2 images")

        img_list_tensor = []
        for img in img_list:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_tensor = transforms.ToTensor()(img).unsqueeze(0).to(self.device)
            if self.fp16:
                img_tensor = img_tensor.half()
            img_list_tensor.append(img_tensor)

        inp = torch.stack(img_list_tensor, dim=1)

        out = self.inference(inp, timestep=0.5, scale=1.0)

        # Convert to numpy image list
        results_list = []

        img = out.squeeze(0).permute(1, 2, 0).cpu().numpy()
        img = (img * 255).clip(0, 255).astype("uint8")
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        results_list.append(img)

        return results_list

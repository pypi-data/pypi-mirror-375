from typing import Any, Optional, Union

import torch

from ccvfi.config import CONFIG_REGISTRY
from ccvfi.model import MODEL_REGISTRY
from ccvfi.type import BaseConfig, ConfigType


class AutoModel:
    @staticmethod
    def from_pretrained(
        pretrained_model_name: Union[ConfigType, str],
        device: Optional[torch.device] = None,
        fp16: bool = True,
        compile: bool = False,
        compile_backend: Optional[str] = None,
        model_dir: Optional[str] = None,
        gh_proxy: Optional[str] = None,
    ) -> Any:
        """
        Get a model instance from a pretrained model name.

        :param pretrained_model_name: The name of the pretrained model. It should be registered in CONFIG_REGISTRY.
        :param device: inference device
        :param fp16: use fp16 precision or not
        :param compile: use torch.compile or not
        :param compile_backend: backend of torch.compile
        :param model_dir: The path to cache the downloaded model. Should be a full path. If None, use default cache path.
        :param gh_proxy: The proxy for downloading from github release. Example: https://github.abskoop.workers.dev/
        :return:
        """

        config = CONFIG_REGISTRY.get(pretrained_model_name)
        return AutoModel.from_config(
            config=config,
            device=device,
            fp16=fp16,
            compile=compile,
            compile_backend=compile_backend,
            model_dir=model_dir,
            gh_proxy=gh_proxy,
        )

    @staticmethod
    def from_config(
        config: Union[BaseConfig, Any],
        device: Optional[torch.device] = None,
        fp16: bool = True,
        compile: bool = False,
        compile_backend: Optional[str] = None,
        model_dir: Optional[str] = None,
        gh_proxy: Optional[str] = None,
    ) -> Any:
        """
        Get a model instance from a config.

        :param config: The config object. It should be registered in CONFIG_REGISTRY.
        :param device: inference device
        :param fp16: use fp16 precision or not
        :param compile: use torch.compile or not
        :param compile_backend: backend of torch.compile
        :param model_dir: The path to cache the downloaded model. Should be a full path. If None, use default cache path.
        :param gh_proxy: The proxy for downloading from github release. Example: https://github.abskoop.workers.dev/
        :return:
        """

        model = MODEL_REGISTRY.get(config.model)
        model = model(
            config=config,
            device=device,
            fp16=fp16,
            compile=compile,
            compile_backend=compile_backend,
            model_dir=model_dir,
            gh_proxy=gh_proxy,
        )

        return model

    @staticmethod
    def register(obj: Optional[Any] = None, name: Optional[str] = None) -> Any:
        """
        Register the given object under the name `obj.__name__` or the given name.
        Can be used as either a decorator or not. See docstring of this class for usage.

        :param obj: The object to register. If None, this is being used as a decorator.
        :param name: The name to register the object under. If None, use `obj.__name__`.
        :return:
        """
        if obj is None:
            # used as a decorator
            def deco(func_or_class: Any) -> Any:
                _name = name
                if _name is None:
                    _name = func_or_class.__name__
                MODEL_REGISTRY.register(obj=func_or_class, name=_name)
                return func_or_class

            return deco

        # used as a function call
        if name is None:
            name = obj.__name__
        MODEL_REGISTRY.register(obj=obj, name=name)

from ccrestoration.util.registry import Registry

ARCH_REGISTRY: Registry = Registry("ARCH")

from ccrestoration.arch.rrdb_arch import RRDBNet  # noqa
from ccrestoration.arch.srvgg_arch import SRVGGNetCompact  # noqa
from ccrestoration.arch.upcunet_arch import UpCunet  # noqa
from ccrestoration.arch.edsr_arch import EDSR  # noqa
from ccrestoration.arch.swinir_arch import SwinIR  # noqa
from ccrestoration.arch.edvr_arch import EDVR, EDVRFeatureExtractor  # noqa
from ccrestoration.arch.spynet_arch import SpyNet  # noqa
from ccrestoration.arch.basicvsr_arch import BasicVSR  # noqa
from ccrestoration.arch.iconvsr_arch import IconVSR  # noqa
from ccrestoration.arch.msrswvsr_arch import MSRSWVSR  # noqa
from ccrestoration.arch.scunet_arch import SCUNet  # noqa
from ccrestoration.arch.dat_arch import DAT  # noqa
from ccrestoration.arch.srcnn_arch import SRCNN  # noqa
from ccrestoration.arch.hat_arch import HAT  # noqa

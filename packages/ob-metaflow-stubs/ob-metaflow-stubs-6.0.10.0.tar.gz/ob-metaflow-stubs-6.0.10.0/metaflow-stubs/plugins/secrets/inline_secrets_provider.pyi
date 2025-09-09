######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.2.1+obcheckpoint(0.2.4);ob(v1)                                                    #
# Generated on 2025-09-08T21:00:14.411655                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import abc
import typing
if typing.TYPE_CHECKING:
    import abc
    import metaflow.plugins.secrets

from . import SecretsProvider as SecretsProvider

class InlineSecretsProvider(metaflow.plugins.secrets.SecretsProvider, metaclass=abc.ABCMeta):
    def get_secret_as_dict(self, secret_id, options = {}, role = None):
        """
        Intended to be used for testing purposes only.
        """
        ...
    ...


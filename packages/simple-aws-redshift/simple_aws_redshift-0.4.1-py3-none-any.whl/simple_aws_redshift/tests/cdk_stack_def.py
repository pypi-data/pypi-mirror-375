# -*- coding: utf-8 -*-

import cdkit.api as cdkit

from constructs import Construct

from .cdk_construct_def import (
    ExperimentRedshiftServerlessParams,
    ExperimentRedshiftServerless,
)


class ExperimentRedshiftServerlessStack(cdkit.BaseStack):
    def __init__(
        self,
        scope: Construct,
        params: cdkit.StackParams,
        experiment_redshift_serverless_params: ExperimentRedshiftServerlessParams,
    ):
        super().__init__(scope=scope, params=params)
        self.params = params
        self.experiment_redshift_serverless = ExperimentRedshiftServerless(
            scope=self,
            params=experiment_redshift_serverless_params,
        )

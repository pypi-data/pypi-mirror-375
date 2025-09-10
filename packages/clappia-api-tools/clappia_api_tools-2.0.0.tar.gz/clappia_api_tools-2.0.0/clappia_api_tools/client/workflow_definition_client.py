from typing import Dict, Any, Optional
from .base_client import BaseClappiaClient
from clappia_api_tools.utils.logging_utils import get_logger

from clappia_api_tools.models.request import (
    UpsertAiWorkflowStepRequest,
    UpsertApprovalWorkflowStepRequest,
    UpsertCodeWorkflowStepRequest,
    UpsertConditionWorkflowStepRequest,
    UpsertDatabaseWorkflowStepRequest,
    UpsertEmailWorkflowStepRequest,
    UpsertLoopWorkflowStepRequest,
    UpsertMobileNotificationWorkflowStepRequest,
    UpsertRestApiWorkflowStepRequest,
    UpsertSlackWorkflowStepRequest,
    UpsertSmsWorkflowStepRequest,
    UpsertWaitWorkflowStepRequest,
    UpsertWhatsAppWorkflowStepRequest,
    UpsertCreateSubmissionWorkflowStepRequest,
    UpsertDeleteSubmissionWorkflowStepRequest,
    UpsertFindSubmissionWorkflowStepRequest,
    UpsertEditSubmissionWorkflowStepRequest,
)
from clappia_api_tools.models.response import (
    WorkflowResponse,
    WorkflowStepResponse,
    BaseResponse,
)
from clappia_api_tools.enums import TriggerType, NodeType

logger = get_logger(__name__)


class WorkflowDefinitionClient(BaseClappiaClient):
    """Client for managing Clappia workflow definitions.

    This client handles retrieving and managing workflow definitions, including
    getting workflows, adding workflow steps, removing workflow steps,
    updating workflow steps, and reordering workflow steps.
    """

    def get_workflow(self, app_id: str, trigger_type: str) -> WorkflowResponse:
        """Get a workflow definition for a specific app and trigger type"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                operation="get_workflow",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                operation="get_workflow",
            )

        params = {
            "appId": app_id,
            "triggerType": trigger_type,
        }

        logger.info(
            f"Getting workflow for app_id: {app_id} with trigger_type: {trigger_type}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="GET", endpoint="workflowdefinitionv2/getWorkflow", params=params
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="get_workflow",
            )

        return WorkflowResponse(
            success=True,
            message="Successfully retrieved workflow definition",
            app_id=app_id,
            data=response_data,
            operation="get_workflow",
        )

    def add_ai_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertAiWorkflowStepRequest,
        step_variable_name: Optional[str] = None,
        parent_step_variable_name: Optional[str] = None,
    ) -> WorkflowStepResponse:
        """Add an AI workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_ai_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_ai_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.AI_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name

        logger.info(
            f"Adding AI workflow step to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/addWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_ai_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully added AI workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="add_ai_step",
            step_variable_name=step_variable_name,
            parent_step_variable_name=parent_step_variable_name,
            data=response_data,
        )

    def update_ai_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertAiWorkflowStepRequest,
    ) -> WorkflowStepResponse:
        """Update an AI workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_ai_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_ai_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating AI workflow step in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/updateWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_ai_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully updated AI workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="update_ai_step",
            step_variable_name=step_variable_name,
            data=response_data,
        )

    def reorder_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        parent_step_variable_name: str,
    ) -> WorkflowStepResponse:
        """Reorder a workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="reorder",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="reorder",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            "parentVariableName": parent_step_variable_name,
        }

        logger.info(
            f"Reordering workflow step for app_id: {app_id} with step: {step_variable_name}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/reorderWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="reorder",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully reordered workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="reorder",
            step_variable_name=step_variable_name,
            parent_step_variable_name=parent_step_variable_name,
            data=response_data,
        )

    # Approval Workflow Step Methods
    def add_approval_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertApprovalWorkflowStepRequest,
        step_variable_name: Optional[str] = None,
        parent_step_variable_name: Optional[str] = None,
    ) -> WorkflowStepResponse:
        """Add an approval workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_approval_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_approval_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.APPROVAL_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name

        logger.info(
            f"Adding approval workflow step to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/addWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_approval_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully added approval workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="add_approval_step",
            step_variable_name=step_variable_name,
            parent_step_variable_name=parent_step_variable_name,
            data=response_data,
        )

    def update_approval_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertApprovalWorkflowStepRequest,
    ) -> WorkflowStepResponse:
        """Update an approval workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_approval_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_approval_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating approval workflow step in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/updateWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_approval_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully updated approval workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="update_approval_step",
            step_variable_name=step_variable_name,
            data=response_data,
        )

    # Code Workflow Step Methods
    def add_code_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertCodeWorkflowStepRequest,
        step_variable_name: Optional[str] = None,
        parent_step_variable_name: Optional[str] = None,
    ) -> WorkflowStepResponse:
        """Add a code workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_code_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_code_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.CODE_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name

        logger.info(
            f"Adding code workflow step to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/addWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_code_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully added code workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="add_code_step",
            step_variable_name=step_variable_name,
            parent_step_variable_name=parent_step_variable_name,
            data=response_data,
        )

    def update_code_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertCodeWorkflowStepRequest,
    ) -> WorkflowStepResponse:
        """Update a code workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_code_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_code_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating code workflow step in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/updateWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_code_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully updated code workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="update_code_step",
            step_variable_name=step_variable_name,
            data=response_data,
        )

    # Condition Workflow Step Methods
    def add_condition_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertConditionWorkflowStepRequest,
        step_variable_name: Optional[str] = None,
        parent_step_variable_name: Optional[str] = None,
    ) -> WorkflowStepResponse:
        """Add a condition workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_condition_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_condition_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.CONDITION_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name

        logger.info(
            f"Adding condition workflow step to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/addWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_condition_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully added condition workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="add_condition_step",
            step_variable_name=step_variable_name,
            parent_step_variable_name=parent_step_variable_name,
            data=response_data,
        )

    def update_condition_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertConditionWorkflowStepRequest,
    ) -> WorkflowStepResponse:
        """Update a condition workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_condition_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_condition_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating condition workflow step in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/updateWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_condition_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully updated condition workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="update_condition_step",
            step_variable_name=step_variable_name,
            data=response_data,
        )

    # Database Workflow Step Methods
    def add_database_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertDatabaseWorkflowStepRequest,
        step_variable_name: Optional[str] = None,
        parent_step_variable_name: Optional[str] = None,
    ) -> WorkflowStepResponse:
        """Add a database workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_database_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_database_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.DATABASE_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name

        logger.info(
            f"Adding database workflow step to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/addWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_database_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully added database workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="add_database_step",
            step_variable_name=step_variable_name,
            parent_step_variable_name=parent_step_variable_name,
            data=response_data,
        )

    def update_database_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertDatabaseWorkflowStepRequest,
    ) -> WorkflowStepResponse:
        """Update a database workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_database_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_database_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating database workflow step in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/updateWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_database_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully updated database workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="update_database_step",
            step_variable_name=step_variable_name,
            data=response_data,
        )

    # Email Workflow Step Methods
    def add_email_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertEmailWorkflowStepRequest,
        step_variable_name: Optional[str] = None,
        parent_step_variable_name: Optional[str] = None,
    ) -> WorkflowStepResponse:
        """Add an email workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_email_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_email_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.EMAIL_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name

        logger.info(
            f"Adding email workflow step to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/addWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_email_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully added email workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="add_email_step",
            step_variable_name=step_variable_name,
            parent_step_variable_name=parent_step_variable_name,
            data=response_data,
        )

    def update_email_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertEmailWorkflowStepRequest,
    ) -> WorkflowStepResponse:
        """Update an email workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_email_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_email_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating email workflow step in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/updateWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_email_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully updated email workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="update_email_step",
            step_variable_name=step_variable_name,
            data=response_data,
        )

    # Loop Workflow Step Methods
    def add_loop_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertLoopWorkflowStepRequest,
        step_variable_name: Optional[str] = None,
        parent_step_variable_name: Optional[str] = None,
    ) -> WorkflowStepResponse:
        """Add a loop workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_loop_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_loop_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.LOOP_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name

        logger.info(
            f"Adding loop workflow step to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/addWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_loop_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully added loop workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="add_loop_step",
            step_variable_name=step_variable_name,
            parent_step_variable_name=parent_step_variable_name,
            data=response_data,
        )

    def update_loop_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertLoopWorkflowStepRequest,
    ) -> WorkflowStepResponse:
        """Update a loop workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_loop_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_loop_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating loop workflow step in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/updateWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_loop_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully updated loop workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="update_loop_step",
            step_variable_name=step_variable_name,
            data=response_data,
        )

    # Mobile Notification Workflow Step Methods
    def add_mobile_notification_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertMobileNotificationWorkflowStepRequest,
        step_variable_name: Optional[str] = None,
        parent_step_variable_name: Optional[str] = None,
    ) -> WorkflowStepResponse:
        """Add a mobile notification workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_mobile_notification_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_mobile_notification_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.MOBILE_NOTIFICATION_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name

        logger.info(
            f"Adding mobile notification workflow step to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/addWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_mobile_notification_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully added mobile notification workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="add_mobile_notification_step",
            step_variable_name=step_variable_name,
            parent_step_variable_name=parent_step_variable_name,
            data=response_data,
        )

    def update_mobile_notification_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertMobileNotificationWorkflowStepRequest,
    ) -> WorkflowStepResponse:
        """Update a mobile notification workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_mobile_notification_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_mobile_notification_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating mobile notification workflow step in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/updateWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_mobile_notification_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully updated mobile notification workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="update_mobile_notification_step",
            step_variable_name=step_variable_name,
            data=response_data,
        )

    # REST API Workflow Step Methods
    def add_rest_api_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertRestApiWorkflowStepRequest,
        step_variable_name: Optional[str] = None,
        parent_step_variable_name: Optional[str] = None,
    ) -> WorkflowStepResponse:
        """Add a REST API workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_rest_api_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_rest_api_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.REST_API_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name

        logger.info(
            f"Adding REST API workflow step to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/addWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_rest_api_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully added REST API workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="add_rest_api_step",
            step_variable_name=step_variable_name,
            parent_step_variable_name=parent_step_variable_name,
            data=response_data,
        )

    def update_rest_api_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertRestApiWorkflowStepRequest,
    ) -> WorkflowStepResponse:
        """Update a REST API workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_rest_api_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_rest_api_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating REST API workflow step in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/updateWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_rest_api_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully updated REST API workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="update_rest_api_step",
            step_variable_name=step_variable_name,
            data=response_data,
        )

    # Slack Workflow Step Methods
    def add_slack_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertSlackWorkflowStepRequest,
        step_variable_name: Optional[str] = None,
        parent_step_variable_name: Optional[str] = None,
    ) -> WorkflowStepResponse:
        """Add a Slack workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_slack_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_slack_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.SLACK_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name

        logger.info(
            f"Adding Slack workflow step to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/addWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_slack_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully added Slack workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="add_slack_step",
            step_variable_name=step_variable_name,
            parent_step_variable_name=parent_step_variable_name,
            data=response_data,
        )

    def update_slack_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertSlackWorkflowStepRequest,
    ) -> WorkflowStepResponse:
        """Update a Slack workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_slack_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_slack_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating Slack workflow step in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/updateWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_slack_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully updated Slack workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="update_slack_step",
            step_variable_name=step_variable_name,
            data=response_data,
        )

    # SMS Workflow Step Methods
    def add_sms_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertSmsWorkflowStepRequest,
        step_variable_name: Optional[str] = None,
        parent_step_variable_name: Optional[str] = None,
    ) -> WorkflowStepResponse:
        """Add an SMS workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_sms_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_sms_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.SMS_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name

        logger.info(
            f"Adding SMS workflow step to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/addWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_sms_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully added SMS workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="add_sms_step",
            step_variable_name=step_variable_name,
            parent_step_variable_name=parent_step_variable_name,
            data=response_data,
        )

    def update_sms_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertSmsWorkflowStepRequest,
    ) -> WorkflowStepResponse:
        """Update an SMS workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_sms_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_sms_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating SMS workflow step in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/updateWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_sms_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully updated SMS workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="update_sms_step",
            step_variable_name=step_variable_name,
            data=response_data,
        )

    # Wait Workflow Step Methods
    def add_wait_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertWaitWorkflowStepRequest,
        step_variable_name: Optional[str] = None,
        parent_step_variable_name: Optional[str] = None,
    ) -> WorkflowStepResponse:
        """Add a wait workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_wait_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_wait_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.WAIT_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name

        logger.info(
            f"Adding wait workflow step to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/addWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_wait_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully added wait workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="add_wait_step",
            step_variable_name=step_variable_name,
            parent_step_variable_name=parent_step_variable_name,
            data=response_data,
        )

    def update_wait_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertWaitWorkflowStepRequest,
    ) -> WorkflowStepResponse:
        """Update a wait workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_wait_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_wait_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating wait workflow step in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/updateWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_wait_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully updated wait workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="update_wait_step",
            step_variable_name=step_variable_name,
            data=response_data,
        )

    # WhatsApp Workflow Step Methods
    def add_whatsapp_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertWhatsAppWorkflowStepRequest,
        step_variable_name: Optional[str] = None,
        parent_step_variable_name: Optional[str] = None,
    ) -> WorkflowStepResponse:
        """Add a WhatsApp workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_whatsapp_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_whatsapp_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.WHATSAPP_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name

        logger.info(
            f"Adding WhatsApp workflow step to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/addWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_whatsapp_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully added WhatsApp workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="add_whatsapp_step",
            step_variable_name=step_variable_name,
            parent_step_variable_name=parent_step_variable_name,
            data=response_data,
        )

    def update_whatsapp_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertWhatsAppWorkflowStepRequest,
    ) -> WorkflowStepResponse:
        """Update a WhatsApp workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_whatsapp_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_whatsapp_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating WhatsApp workflow step in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/updateWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_whatsapp_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully updated WhatsApp workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="update_whatsapp_step",
            step_variable_name=step_variable_name,
            data=response_data,
        )

    # Create Submission Workflow Step Methods
    def add_create_submission_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertCreateSubmissionWorkflowStepRequest,
        step_variable_name: Optional[str] = None,
        parent_step_variable_name: Optional[str] = None,
    ) -> WorkflowStepResponse:
        """Add a create submission workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_create_submission_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_create_submission_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.CREATE_SUBMISSION_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name

        logger.info(
            f"Adding create submission workflow step to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/addWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_create_submission_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully added create submission workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="add_create_submission_step",
            step_variable_name=step_variable_name,
            parent_step_variable_name=parent_step_variable_name,
            data=response_data,
        )

    def update_create_submission_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertCreateSubmissionWorkflowStepRequest,
    ) -> WorkflowStepResponse:
        """Update a create submission workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_create_submission_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_create_submission_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating create submission workflow step in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/updateWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_create_submission_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully updated create submission workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="update_create_submission_step",
            step_variable_name=step_variable_name,
            data=response_data,
        )

    # Delete Submission Workflow Step Methods
    def add_delete_submission_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertDeleteSubmissionWorkflowStepRequest,
        step_variable_name: Optional[str] = None,
        parent_step_variable_name: Optional[str] = None,
    ) -> WorkflowStepResponse:
        """Add a delete submission workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_delete_submission_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_delete_submission_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.DELETE_SUBMISSION_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name

        logger.info(
            f"Adding delete submission workflow step to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/addWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_delete_submission_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully added delete submission workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="add_delete_submission_step",
            step_variable_name=step_variable_name,
            parent_step_variable_name=parent_step_variable_name,
            data=response_data,
        )

    def update_delete_submission_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertDeleteSubmissionWorkflowStepRequest,
    ) -> WorkflowStepResponse:
        """Update a delete submission workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_delete_submission_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_delete_submission_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating delete submission workflow step in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/updateWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_delete_submission_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully updated delete submission workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="update_delete_submission_step",
            step_variable_name=step_variable_name,
            data=response_data,
        )

    # Find Submission Workflow Step Methods
    def add_find_submission_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertFindSubmissionWorkflowStepRequest,
        step_variable_name: Optional[str] = None,
        parent_step_variable_name: Optional[str] = None,
    ) -> WorkflowStepResponse:
        """Add a find submission workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_find_submission_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_find_submission_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.FIND_SUBMISSION_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name

        logger.info(
            f"Adding find submission workflow step to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/addWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_find_submission_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully added find submission workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="add_find_submission_step",
            step_variable_name=step_variable_name,
            parent_step_variable_name=parent_step_variable_name,
            data=response_data,
        )

    def update_find_submission_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertFindSubmissionWorkflowStepRequest,
    ) -> WorkflowStepResponse:
        """Update a find submission workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_find_submission_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_find_submission_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating find submission workflow step in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/updateWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_find_submission_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully updated find submission workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="update_find_submission_step",
            step_variable_name=step_variable_name,
            data=response_data,
        )

    # Edit Submission Workflow Step Methods
    def add_edit_submission_step(
        self,
        app_id: str,
        trigger_type: str,
        request: UpsertEditSubmissionWorkflowStepRequest,
        step_variable_name: Optional[str] = None,
        parent_step_variable_name: Optional[str] = None,
    ) -> WorkflowStepResponse:
        """Add an edit submission workflow step to a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_edit_submission_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_edit_submission_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "nodeType": NodeType.EDIT_SUBMISSION_NODE.value,
            **request.to_json(),
        }
        if step_variable_name is not None:
            payload["stepVariableName"] = step_variable_name
        if parent_step_variable_name is not None:
            payload["parentVariableName"] = parent_step_variable_name

        logger.info(
            f"Adding edit submission workflow step to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/addWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="add_edit_submission_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully added edit submission workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="add_edit_submission_step",
            step_variable_name=step_variable_name,
            parent_step_variable_name=parent_step_variable_name,
            data=response_data,
        )

    def update_edit_submission_step(
        self,
        app_id: str,
        trigger_type: str,
        step_variable_name: str,
        request: UpsertEditSubmissionWorkflowStepRequest,
    ) -> WorkflowStepResponse:
        """Update an edit submission workflow step in a Clappia app"""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkflowStepResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_edit_submission_step",
            )

        if trigger_type not in [t.value for t in TriggerType]:
            return WorkflowStepResponse(
                success=False,
                message=f"Invalid trigger type: {trigger_type}, allowed types are: {', '.join([t.value for t in TriggerType])}",
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_edit_submission_step",
            )

        payload = {
            "appId": app_id,
            "triggerType": trigger_type,
            "stepVariableName": step_variable_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating edit submission workflow step in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workflowdefinitionv2/updateWorkflowStep",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkflowStepResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                trigger_type=trigger_type,
                operation="update_edit_submission_step",
            )

        return WorkflowStepResponse(
            success=True,
            message="Successfully updated edit submission workflow step",
            app_id=app_id,
            trigger_type=trigger_type,
            operation="update_edit_submission_step",
            step_variable_name=step_variable_name,
            data=response_data,
        )

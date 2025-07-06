from fastapi import APIRouter, HTTPException, Depends
from ..schemas.workflow_state import WorkflowRequest, HumanInputRequest, WorkflowResponse
from ..services.workflow_service import WorkflowService
from typing import Dict, Any

router = APIRouter(prefix="/workflows", tags=["workflows"])

# Dependency to get workflow service
def get_workflow_service():
    return WorkflowService()

@router.post("/start", response_model=WorkflowResponse)
async def start_workflow(
    request: WorkflowRequest,
    workflow_service: WorkflowService = Depends(get_workflow_service)
):
    """Start a new workflow"""
    try:
        result = await workflow_service.start_workflow(request)
        return WorkflowResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{thread_id}/input", response_model=WorkflowResponse)
async def provide_human_input(
    thread_id: str,
    request: HumanInputRequest,
    workflow_service: WorkflowService = Depends(get_workflow_service)
):
    """Provide human input to continue workflow"""
    try:
        request.thread_id = thread_id
        result = await workflow_service.provide_human_input(request)
        return WorkflowResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{thread_id}/status", response_model=Dict[str, Any])
async def get_workflow_status(
    thread_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service)
):
    """Get workflow status"""
    try:
        result = await workflow_service.get_workflow_status(thread_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{thread_id}/state", response_model=Dict[str, Any])
async def get_workflow_state(
    thread_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service)
):
    """Get complete workflow state"""
    try:
        result = await workflow_service.get_workflow_status(thread_id)
        if result.get("status") == "not_found":
            raise HTTPException(status_code=404, detail="Workflow not found")
        return result.get("state", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{thread_id}/approve/hashnode", response_model=WorkflowResponse)
async def approve_hashnode_publishing(
    thread_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service)
):
    """Approve Hashnode publishing"""
    try:
        request = HumanInputRequest(
            thread_id=thread_id,
            user_input="yes",
            action="approve"
        )
        result = await workflow_service.provide_human_input(request)
        return WorkflowResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{thread_id}/reject/hashnode", response_model=WorkflowResponse)
async def reject_hashnode_publishing(
    thread_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service)
):
    """Reject Hashnode publishing"""
    try:
        request = HumanInputRequest(
            thread_id=thread_id,
            user_input="no",
            action="reject"
        )
        result = await workflow_service.provide_human_input(request)
        return WorkflowResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{thread_id}/approve/twitter", response_model=WorkflowResponse)
async def approve_twitter_publishing(
    thread_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service)
):
    """Approve Twitter publishing"""
    try:
        request = HumanInputRequest(
            thread_id=thread_id,
            user_input="yes",
            action="approve"
        )
        result = await workflow_service.provide_human_input(request)
        return WorkflowResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{thread_id}/reject/twitter", response_model=WorkflowResponse)
async def reject_twitter_publishing(
    thread_id: str,
    workflow_service: WorkflowService = Depends(get_workflow_service)
):
    """Reject Twitter publishing"""
    try:
        request = HumanInputRequest(
            thread_id=thread_id,
            user_input="no",
            action="reject"
        )
        result = await workflow_service.provide_human_input(request)
        return WorkflowResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
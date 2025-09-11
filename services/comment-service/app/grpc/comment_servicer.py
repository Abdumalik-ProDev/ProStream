from app.grpc import comment_pb2, comment_pb2_grpc
from app.services import comment_service
from app.core.db import SessionLocal
import grpc

class CommentServicer(comment_pb2_grpc.CommentServiceServicer):
    async def GetCommentsByVideo(self, request, context):
        items, total = await comment_service.list_comments(request.video_id, limit=request.limit or 20, offset=request.offset or 0)
        reply_items = []
        for it in items:
            reply_items.append(comment_pb2.CommentItem(
                id=it.id,
                user_id=it.user_id,
                video_id=it.video_id,
                parent_id=it.parent_id or "",
                content=it.content,
                is_hidden=it.is_hidden,
                created_at=int(it.created_at.timestamp())
            ))
        return comment_pb2.CommentListReply(items=reply_items, total=total)

    async def CreateComment(self, request, context):
        from app.schemes.comment import CommentCreate
        payload = CommentCreate(video_id=request.video_id, parent_id=request.parent_id or None, content=request.content)
        created = await comment_service.create_comment(request.user_id, payload)
        return comment_pb2.CommentReply(id=created.id, status="created")
    
    async def ReadComment(self, request, context):
        comment = await comment_service.get_comment(request.comment_id)
        if not comment:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Comment not found')
            return comment_pb2.CommentReply()
        return comment_pb2.CommentReply(
            id=comment.id,
            user_id=comment.user_id,
            video_id=comment.video_id,
            parent_id=comment.parent_id or "",
            content=comment.content,
            is_hidden=comment.is_hidden,
            created_at=int(comment.created_at.timestamp())
        )
    
    async def UpdateComment(self, request, context):
        from app.schemes.comment import CommentUpdate
        payload = CommentUpdate(
            content=request.content if request.content else None,
            is_hidden=request.is_hidden if request.is_hidden else None
        )
        updated = await comment_service.update_comment(request.comment_id, payload)
        if not updated:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Comment not found')
            return comment_pb2.CommentReply()
        return comment_pb2.CommentReply(
            id=updated.id,
            user_id=updated.user_id,
            video_id=updated.video_id,
            parent_id=updated.parent_id or "",
            content=updated.content,
            is_hidden=updated.is_hidden,
            created_at=int(updated.created_at.timestamp())
        )
    
    async def DeleteComment(self, request, context):
        deleted = await comment_service.delete_comment(request.comment_id)
        if not deleted:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Comment not found')
            return comment_pb2.CommentReply()
        return comment_pb2.CommentReply(id=deleted.id, status="deleted")
    
    async def ListReplies(self, request):
        items, total = await comment_service.list_replies(request.parent_id, limit=request.limit or 20, offset=request.offset or 0)
        reply_items = []
        for it in items:
            reply_items.append(comment_pb2.CommentItem(
                id=it.id,
                user_id=it.user_id,
                video_id=it.video_id,
                parent_id=it.parent_id or "",
                content=it.content,
                is_hidden=it.is_hidden,
                created_at=int(it.created_at.timestamp())
            ))
        return comment_pb2.CommentListReply(items=reply_items, total=total)
from fastmcp.server.middleware import Middleware, MiddlewareContext

class LoggingMiddleware(Middleware):
    
    async def on_message(self, context: MiddlewareContext, call_next):
        LoggingMiddleware.__log__(f"Processing {context.method} from {context.source}")
        
        result = await call_next(context)
        
        LoggingMiddleware.__log__(f"Completed {context.method}")
        
        return result
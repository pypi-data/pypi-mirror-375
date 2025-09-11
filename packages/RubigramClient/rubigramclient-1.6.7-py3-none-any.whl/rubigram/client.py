from typing import Optional, Callable, Union
from rubigram.types import Update, InlineMessage
from rubigram.method import Method
from rubigram.filters import Filter
from rubigram.state import StateManager
from datetime import datetime
from aiohttp.web import Application, Request, json_response, run_app
import asyncio
import logging


logging.basicConfig(
    format="%(asctime)s | %(levelname)s : %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG
)

logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)


class Client(Method):
    def __init__(
        self,
        token: str,
        endpoint: Optional[str] = None,
        host: str = "0.0.0.0",
        port: int = 8000
    ):
        self.token = token
        self.endpoint = endpoint
        self.host = host
        self.port = port
        self.offset_id = None
        self.set_endpoint = True
        self.ROUTES = []
        self.MESSAGE_HANDLER = []
        self.INLINE_HANDLER = []
        self.state = StateManager()
        super().__init__(token)
        
    
    def on_message(self, filters: Optional[Filter] = None):
        def decorator(func: Callable) -> Callable:
            async def wrapper(client: Client, update: Update):
                if filters is None or await filters(update):
                    await func(client, update)
                    return True
                return False
            self.MESSAGE_HANDLER.append(wrapper)
            return func
        return decorator

    def on_inline_message(self, filters: Optional[Filter] = None):
        def decorator(func: Callable) -> Callable:
            async def wrapper(client: Client, update: Update):
                if filters is None or await filters(update):
                    await func(client, update)
                    return True
                return False
            self.INLINE_HANDLER.append(wrapper)
            return func
        return decorator

    def on_create_app(self, path: str, method: str = "GET"):
        def decorator(func):
            self.ROUTES.append((path, func, method.upper()))
            return func
        return decorator
    
    async def dispatch(self, update: Union[Update, InlineMessage]):
        handlers = self.MESSAGE_HANDLER if isinstance(update, Update) else self.INLINE_HANDLER
        for handler in handlers:
            matched = await handler(self, update)
            if matched:
                return
            
    async def updater(self, data: dict):
        if "inline_message" in data:
            event = InlineMessage.from_dict(data["inline_message"])
        elif "update" in data:
            event = Update.from_dict(data["update"])
        else: return
        event.client = self
        await self.dispatch(event)
        
    async def set_endpoints(self):
        endpoint_type = ["ReceiveUpdate", "ReceiveInlineMessage"]
        for i in endpoint_type:
            set_endpoint = await self.update_bot_endpoint(f"{self.endpoint}/{i}", i)
            logging.info(f"status set endpoint for {i} : {set_endpoint["status"]}")
        
    async def on_startup(self, app):
        if self.set_endpoint:
            await self.set_endpoints()
        await self.start()

    async def on_cleanup(self, app):
        await self.stop()
        
    def create_request_handler(self):
        async def wrapper(request: Request):
            data = await request.json()
            await self.updater(data)
            return json_response({"status": "OK"})
        return wrapper


    async def update_runner(self):
        try:
            while True:
                get_update = await self.get_update(100, self.offset_id)
                updates = get_update.updates
                if updates:
                    for update in updates:
                        time = update.new_message.time if update.type == "NewMessage" else update.updated_message.time if update.type == "UpdatedMessage" else None
                        time = int(time)
                        now = int(datetime.now().timestamp())
                        if time and (time >= now or time + 2 >= now):
                            update.client = self
                            await self.dispatch(update)
                    self.offset_id = get_update.next_offset_id
        except Exception as error:
            logging.error(error)
        finally:
            await self.stop()
    
    def run(self, set_endpoint = True):
        self.set_endpoint = set_endpoint
        if self.endpoint:
            app = Application()
            app.on_startup(self.on_startup)
            app.on_cleanup(self.on_cleanup)
            
            app.router.add_post("/ReceiveUpdate", self.create_request_handler())
            app.router.add_post("/ReceiveInlineMessage", self.create_request_handler())
            
            for path, func, method in self.ROUTES:
                match method:
                    case "GET":
                        app.router.add_get(path, func)
                    case "POST":
                        app.router.add_post(path, func)
                    case "DELETE":
                        app.router.add_delete(path, func)
                    case "PUT":
                        app.router.add_put(path, func)
                    case "PATCH":
                        app.router.add_patch(path, func)
                        
            run_app(app, host=self.host, port=self.port)

        else:
            try:
                logging.info("Start Bot")
                asyncio.run(self.update_runner())
            except KeyboardInterrupt:
                logging.info("Stop Bot")
            except Exception as error:
                logging.error(error)
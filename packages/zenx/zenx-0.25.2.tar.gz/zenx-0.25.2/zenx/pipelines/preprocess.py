from typing import Any, Dict

from zenx.pipelines.base import Pipeline
from zenx.exceptions import DropItem
from zenx.utils import log_processing_time



class PreprocessPipeline(Pipeline):
    name = "preprocess"
    required_settings = []


    async def open(self) -> None: 
        self.logger.info("opened", pipeline=self.name) 
    
    
    @log_processing_time
    async def process_item(self, item: Dict, producer: str) -> Dict:
        _id = item.get("_id")
        if _id:
            inserted = await self.db.insert(_id, producer)
            if not inserted:
                raise DropItem

        if "scraped_at" in item and "responded_at" in item:
            scraped_time = item['scraped_at'] - item['responded_at']
            self.logger.info("scraped", id=item.get("_id"), item=item, time_ms=scraped_time)
        else:
            self.logger.info("scraped", id=item.get("_id"), item=item)
            
        if self.settings.MAX_SCRAPE_DELAY > 0:
            self.drop_if_scraped_too_late(item)
            
        return item
    

    async def send(self, payload: Any) -> None:
        pass


    async def close(self) -> None: 
        self.logger.info("closed", pipeline=self.name)

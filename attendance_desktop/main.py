from api.api_client import get_api_client
from services.campus_service import CampusService
from ui.app import App

if __name__ == "__main__":
    App(CampusService(get_api_client())).mainloop()

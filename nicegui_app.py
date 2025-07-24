# nicegui_app.py

from nicegui import ui
from fastapi import APIRouter

router = APIRouter()

@ui.page('/')
def main_page():
    ui.label('Void Cloud Intelligence Dashboard').style('font-size: 24px; font-weight: bold; margin-bottom: 20px')

    ui.button('Run Deep Dive', on_click=lambda: print('Running deep dive search...')).style('margin-bottom: 10px')
    ui.button('Chat with AI', on_click=lambda: print('Starting AI chat...')).style('margin-bottom: 10px')
    ui.button('Store Memory', on_click=lambda: print('Storing memory session...')).style('margin-bottom: 10px')

    # Placeholder for chat input/output
    with ui.row():
        chat_input = ui.input(placeholder='Type your message here...').style('width: 300px')
        ui.button('Send', on_click=lambda: print(f'User says: {chat_input.value}'))

# Optional route for integration check
@router.get("/nicegui-info")
def info():
    return {"status": "NiceGUI integrated"}

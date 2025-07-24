from selenium import webdriver
from fastapi import APIRouter
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

auto_router = APIRouter()

@auto_router.post('harrell-auto')
def harrell_auto():
    print
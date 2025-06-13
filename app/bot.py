from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from sqlalchemy.orm import Session
from app.database import SessionLocal, create_tables
from app.models import Book
import os
router = Router()

def get_db_session():
    return SessionLocal()

@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(" Salom! Kitoblar botiga xush kelibsiz. /help buyrug'i orqali yordam olishingiz mumkin.")

@router.message(Command("help"))
async def help_handler(message: Message):
    help_text = """
Yordam:

/start - Botni ishga tushirish
/help - Barcha komandalar ro'yxati
/books - Barcha kitoblar ro'yxati
/add_book - Yangi kitob qo'shish (Format: /add_book "sarlavha" "muallif")
/search - Kitoblarni qidirish (Format: /search kalit_soz)
"""
    await message.answer(help_text)

@router.message(Command("books"))
async def books_handler(message: Message):
    db = get_db_session()
    try:
        books = db.query(Book).all()
        if books:
            books_list = "\n".join([f"{book.id}. {book.title} - {book.author}" for book in books])
            await message.answer(f"Kitoblar ro'yxati:\n\n{books_list}")
        else:
            await message.answer(" Hali hech qanday kitob qo'shilmagan.")
    finally:
        db.close()

@router.message(Command("add_book"))
async def add_book_handler(message: Message):
    args = message.text.split('"')[1::2]
    if len(args) != 2:
        await message.answer("Noto'g'ri format! To'g'ri format: /add_book \"sarlavha\" \"muallif\"")
        return

    title, author = args
    db = get_db_session()
    try:
        new_book = Book(title=title, author=author)
        db.add(new_book)
        db.commit()
        await message.answer(f"✅ Yangi kitob qo'shildi:\n{title} - {author}")
    finally:
        db.close()

@router.message(Command("search"))
async def search_handler(message: Message):
    args = message.text.split()[1:]
    if not args:
        await message.answer("❌ Qidiruv uchun kalit so'z kiriting!(Format:/seach kalit_soz)")
        return

    search_query = " ".join(args).lower()
    db = get_db_session()
    try:
        books = db.query(Book).filter(Book.title.ilike(f"%{search_query}%")).all()
        if books:
            result = "\n".join([f"{book.id}. {book.title} - {book.author}" for book in books])
            await message.answer(f"🔍 Qidiruv natijalari:\n\n{result}")
        else:
            await message.answer("❌ Hech narsa topilmadi.")
    finally:
        db.close()


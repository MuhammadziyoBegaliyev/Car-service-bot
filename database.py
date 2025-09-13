from typing import Optional, List
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, Integer, Text, select as sa_select, text, update as sa_update, delete as sa_delete, func
from config import settings

# --- Engine & Session
engine = create_async_engine(settings.database_url, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# --- Base
class Base(DeclarativeBase):
    pass

# --- Models
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(128), default="")
    username: Mapped[str] = mapped_column(String(64), default="")
    phone: Mapped[str] = mapped_column(String(32), default="")
    language: Mapped[str] = mapped_column(String(8), default="uz")

class ServicePoint(Base):
    __tablename__ = "service_points"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Katta kategoriya: 'service' | 'wash' | 'anti_theft' | 'fuel'
    category: Mapped[str] = mapped_column(String(32), index=True)

    # Eski filterlar (foydalanuvchi qismida ishlatiladi)
    sub_type: Mapped[str] = mapped_column(String(32), default="")  # electric/body/motor/...

    # Admin panel uchun ko‘p-qatlamli kategoriyalar (multi-select): "electric,body,align"
    sub_categories: Mapped[str] = mapped_column(Text, default="")

    name: Mapped[str] = mapped_column(String(128))
    address: Mapped[str] = mapped_column(String(256), default="")
    phone: Mapped[str] = mapped_column(String(64), default="")

    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)

    hours: Mapped[str] = mapped_column(String(64), default="09:00-21:00")
    days_off: Mapped[str] = mapped_column(String(128), default="-")  # Yakshanba yoki '-'

    image_url: Mapped[str] = mapped_column(Text, default="https://via.placeholder.com/800x500.png?text=Avtoservis")

    # Admin: bugungi kun uchun vaqtincha yopiq/ochiq flag
    today_closed: Mapped[int] = mapped_column(Integer, default=0)  # 0=open, 1=closed

# --- Init & demo data
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Yumshoq migratsiya har doim chaqirilsa ham zarar qilmaydi
    await admin_create_or_migrate()

    # Demo nuqtalar (faqat bo‘sh bo‘lsa)
    async with SessionLocal() as session:
        existing = (await session.execute(sa_select(func.count(ServicePoint.id)))).scalar_one()
        if existing == 0:
            demo = [
                ("service","electric","⚡ Elektrchi Usta","Toshkent, Chilonzor 9","998901112233",41.285,69.279,"08:00-20:00","https://via.placeholder.com/800x500.png?text=Elektrchi"),
                ("service","body","🛠 Kuzov Ta'miri","Toshkent, Yunusobod 4","998901112244",41.344,69.286,"09:00-21:00","https://via.placeholder.com/800x500.png?text=Kuzov"),
                ("service","motor","🔩 Motorchi Usta","Toshkent, Sergeli 2","998901112255",41.240,69.207,"10:00-22:00","https://via.placeholder.com/800x500.png?text=Motor"),
                ("service","vulcan","🛞 Vulkanizatsiya 24/7","Toshkent, Olmazor","998901112266",41.362,69.194,"00:00-24:00","https://via.placeholder.com/800x500.png?text=Vulkan"),
                ("service","align","🎯 G'ildirak tekislash","Toshkent, Uchtepa","998901112277",41.305,69.180,"09:00-19:00","https://via.placeholder.com/800x500.png?text=Tekislash"),
                ("service","tint","🕶 Tonirovka Pro","Toshkent, Mirobod","998901112288",41.292,69.279,"10:00-20:00","https://via.placeholder.com/800x500.png?text=Tonirovka"),
                ("service","noise","🔇 Shovqin Izolyatsiyasi","Toshkent, Mirzo Ulug'bek","998901112299",41.347,69.334,"09:00-21:00","https://via.placeholder.com/800x500.png?text=Izolyatsiya"),
                ("service","universal","🧰 Universal Usta","Toshkent, Chilonzor","998901112211",41.310,69.250,"09:00-20:00","https://via.placeholder.com/800x500.png?text=Universal"),
                ("wash","", "🧽 Moyka Clean","Toshkent, Sebzar","998909991122",41.317,69.278,"08:00-22:00","https://via.placeholder.com/800x500.png?text=Moyka"),
                ("anti_theft","", "🛡 Bloklashga Qarshi Tizim","Toshkent, Mirabad","998908887766",41.296,69.281,"09:00-20:00","https://via.placeholder.com/800x500.png?text=Anti-Theft"),
                ("fuel","", "⛽ Yoqilg'i Yetkazish Xizmati","Toshkent, Yakkasaroy","998907771122",41.292,69.263,"24/7","https://via.placeholder.com/800x500.png?text=Fuel"),
            ]
            for c,s,n,a,p,la,lo,h,img in demo:
                sp = ServicePoint(
                    category=c, sub_type=s, sub_categories="", name=n, address=a, phone=p,
                    lat=la, lon=lo, hours=h, days_off="-", image_url=img, today_closed=0
                )
                session.add(sp)
            await session.commit()

# --- User helpers
async def upsert_user(tg_id: int, full_name: str, username: str, phone: str, language: str):
    async with SessionLocal() as session:
        user = (await session.execute(sa_select(User).where(User.tg_id == tg_id))).scalar_one_or_none()
        if user is None:
            user = User(tg_id=tg_id, full_name=full_name or "", username=username or "", phone=phone or "", language=language or "uz")
            session.add(user)
        else:
            user.full_name = full_name or user.full_name
            user.username = username or user.username
            user.phone = phone or user.phone
            user.language = language or user.language
        await session.commit()

async def get_user_language(tg_id: int) -> str:
    async with SessionLocal() as session:
        user = (await session.execute(sa_select(User).where(User.tg_id == tg_id))).scalar_one_or_none()
        return user.language if user else "uz"

# --- Nearest finder
async def find_nearest(category: str, lat: float, lon: float, sub_type: Optional[str] = None):
    from utils.haversine import haversine_km
    async with SessionLocal() as session:
        q = sa_select(ServicePoint).where(ServicePoint.category == category)
        if sub_type:
            q = q.where(ServicePoint.sub_type == sub_type)
        rows = (await session.execute(q)).scalars().all()
        ranked = []
        for r in rows:
            d = haversine_km(lat, lon, r.lat, r.lon)
            ranked.append((d, r))
        ranked.sort(key=lambda x: x[0])
        return ranked[:3]

# --- Admin helpers
async def is_admin(tg_id: int) -> bool:
    return tg_id in settings.admin_ids

# Soft-migrate: jadval bor bo‘lsa ham yo‘q ustunlarni qo‘shish
async def admin_create_or_migrate():
    async with SessionLocal() as session:
        # Jadval bo'lmasa yaratish (sinf bilan create_all ham ishlaydi, lekin safety uchun)
        await session.execute(text("""
        CREATE TABLE IF NOT EXISTS service_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            sub_type TEXT,
            sub_categories TEXT,
            name TEXT,
            address TEXT,
            phone TEXT,
            lat REAL,
            lon REAL,
            hours TEXT,
            days_off TEXT,
            image_url TEXT,
            today_closed INTEGER DEFAULT 0
        );
        """))

        # Ustunlarni tekshirish
        pragma = await session.execute(text("PRAGMA table_info(service_points)"))
        cols = {row[1] for row in pragma}  # column name at index 1

        to_add = []
        if "sub_type" not in cols:
            to_add.append("ALTER TABLE service_points ADD COLUMN sub_type TEXT;")
        if "sub_categories" not in cols:
            to_add.append("ALTER TABLE service_points ADD COLUMN sub_categories TEXT;")
        if "days_off" not in cols:
            to_add.append("ALTER TABLE service_points ADD COLUMN days_off TEXT;")
        if "today_closed" not in cols:
            to_add.append("ALTER TABLE service_points ADD COLUMN today_closed INTEGER DEFAULT 0;")

        for sql in to_add:
            try:
                await session.execute(text(sql))
            except Exception:
                # SQLite ALTER TABLE idempotent bo'lmasligi mumkin — xatolarni yutamiz
                pass

        await session.commit()

# --- CRUD for ServicePoint (admin)
async def create_service_point(
    session: AsyncSession,
    name: str, address: str, phone: str, hours: str, days_off: str,
    categories: List[str], lat: float, lon: float, image_url: str, category: str
):
    sub_categories = ",".join(categories) if categories else ""
    sp = ServicePoint(
        name=name,
        address=address,
        phone=phone,
        hours=hours,
        days_off=days_off or "-",
        category=category,
        sub_categories=sub_categories,
        lat=lat,
        lon=lon,
        image_url=image_url or "https://via.placeholder.com/800x500.png?text=Avtoservis",
        today_closed=0
    )
    session.add(sp)
    await session.commit()
    return sp

async def update_service_point(session: AsyncSession, sp_id: int, fields: dict):
    await session.execute(sa_update(ServicePoint).where(ServicePoint.id == sp_id).values(**fields))
    await session.commit()

async def delete_service_point(session: AsyncSession, sp_id: int):
    await session.execute(sa_delete(ServicePoint).where(ServicePoint.id == sp_id))
    await session.commit()

async def fetch_services_page(page: int, page_size: int, category: str = "service"):
    offset = (page - 1) * page_size
    async with SessionLocal() as session:
        q = sa_select(ServicePoint.id, ServicePoint.name)\
            .where(ServicePoint.category == category)\
            .order_by(ServicePoint.id.desc())\
            .offset(offset)\
            .limit(page_size + 1)
        res = await session.execute(q)
        all_rows = res.all()
    has_next = len(all_rows) > page_size
    rows = all_rows[:page_size]
    items = [(r[0], f"#{r[0]} — {r[1]}") for r in rows]
    return items, has_next

async def toggle_service_today_closed(session: AsyncSession, sp_id: int) -> bool:
    q = sa_select(ServicePoint.today_closed).where(ServicePoint.id == sp_id)
    current = (await session.execute(q)).scalar_one_or_none()
    new_val = 0 if current else 1
    await session.execute(sa_update(ServicePoint).where(ServicePoint.id == sp_id).values(today_closed=new_val))
    await session.commit()
    return bool(new_val)

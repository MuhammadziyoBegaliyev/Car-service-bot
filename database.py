from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, Integer, Text, select, func
from config import settings

engine = create_async_engine(settings.database_url, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

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
    category: Mapped[str] = mapped_column(String(32), index=True)  # service, wash, anti_theft, fuel
    sub_type: Mapped[str] = mapped_column(String(32), default="")  # electric/body/motor/...
    name: Mapped[str] = mapped_column(String(128))
    address: Mapped[str] = mapped_column(String(256), default="")
    phone: Mapped[str] = mapped_column(String(64), default="")
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    hours: Mapped[str] = mapped_column(String(64), default="09:00-21:00")
    image_url: Mapped[str] = mapped_column(Text, default="https://via.placeholder.com/800x500.png?text=Avtoservis")

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as session:
        existing = (await session.execute(select(func.count(ServicePoint.id)))).scalar_one()
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
                ("wash","","🧽 Moyka Clean","Toshkent, Sebzar","998909991122",41.317,69.278,"08:00-22:00","https://via.placeholder.com/800x500.png?text=Moyka"),
                ("anti_theft","","🛡 Bloklashga Qarshi Tizim","Toshkent, Mirabad","998908887766",41.296,69.281,"09:00-20:00","https://via.placeholder.com/800x500.png?text=Anti-Theft"),
                ("fuel","","⛽ Yoqilg'i Yetkazish Xizmati","Toshkent, Yakkasaroy","998907771122",41.292,69.263,"24/7","https://via.placeholder.com/800x500.png?text=Fuel"),
            ]
            for c,s,n,a,p,la,lo,h,img in demo:
                session.add(ServicePoint(category=c, sub_type=s, name=n, address=a, phone=p, lat=la, lon=lo, hours=h, image_url=img))
            await session.commit()

# helpers
async def upsert_user(tg_id: int, full_name: str, username: str, phone: str, language: str):
    from sqlalchemy import select as sa_select
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
    from sqlalchemy import select as sa_select
    async with SessionLocal() as session:
        user = (await session.execute(sa_select(User).where(User.tg_id == tg_id))).scalar_one_or_none()
        return user.language if user else "uz"

async def find_nearest(category: str, lat: float, lon: float, sub_type: str|None=None):
    from sqlalchemy import select as sa_select
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

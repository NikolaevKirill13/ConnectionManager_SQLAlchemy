Если вы случайно зашли сюда - вы сами виноваты=) Учтите, я делал менеджер для себя, что-то похожее предварительно
не искал и искать не буду. Пока не буду. Насколько он вообще правильно работает для меня вопрос открытый, да и зачем
оно надо вопрос тоже открытый=) Тестов нет и не предвидится, все на свой страх и риск=)

Пример создания менеджера и его использование.

async_engine_sqlite = create_async_engine(DB_URL, echo=False)
async_session = async_sessionmaker(async_engine_sqlite, expire_on_commit=False, class_=AsyncSession)
async_engine_sqlite2 = create_async_engine(DB_URL2, echo=False)
async_session2 = async_sessionmaker(async_engine_sqlite2, expire_on_commit=False, class_=AsyncSession)

Для вызова

connection = ConnectionManager(session_db1=async_session, session_db2=async_session2)

К функции или роутеру применяем декоратор

@connection.attach_session("session_db1") с одной или несколькими сессиями
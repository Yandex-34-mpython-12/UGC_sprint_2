PATH = 'fixtures'

pytest_plugins = [
    f'{PATH}.aiohttp',
    f'{PATH}.kafka',
    f'{PATH}.user',
]

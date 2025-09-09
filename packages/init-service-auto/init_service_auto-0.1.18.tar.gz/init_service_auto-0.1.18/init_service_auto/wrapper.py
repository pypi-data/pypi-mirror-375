def run():
    from . import agent
    agent.main()

# import importlib

# def run():
#     agent = importlib.import_module("init_service_auto.agent")
#     agent.main()


# import importlib.util
# import sys
# import pathlib

# def run():
#     # Tìm file .so trong cùng thư mục package
#     package_dir = pathlib.Path(__file__).parent
#     so_file = next(package_dir.glob("agent*.so"))
    
#     spec = importlib.util.spec_from_file_location("init_service_auto.agent", so_file)
#     agent = importlib.util.module_from_spec(spec)
#     sys.modules["init_service_auto.agent"] = agent
#     spec.loader.exec_module(agent)

#     agent.main()

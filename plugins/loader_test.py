
import loader;

if __name__ == '__main__':
    # instance = loader.RequestModel(
    #     filename="yao.pdf",
    #     load_dir=False,
    #     dir="./",
    #     ignored_files=[],
    #     # filename="requirements.txt",
    #     db_connection_string="postgres://wangweisheng:postgres@127.0.0.1:5432/quant?sslmode=disable",
    #     table_name="documents",
    #     vector_field="embedding",
    #     content_field="content"
    # )
    # loader.load_file(instance)
    

    instance = loader.RequestModel(
        filename="",
        load_dir=False,
        dir="D:\projects\go\yao\yao-docs\docs",
        ignored_files=[],
        # filename="requirements.txt",
        db_connection_string="postgres://wangweisheng:postgres@127.0.0.1:5432/quant?sslmode=disable",
        table_name="documents",
        vector_field="embedding",
        content_field="content"
    )
    loader.load_dir(instance)

    
   
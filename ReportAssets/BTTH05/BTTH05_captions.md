# Chu thich hinh BTTH05 - Kien truc tai su dung va cau hinh CSDL

| File | Chu thich |
|------|-----------|
| `BTTH05_01_architecture_requirement_flow.png` | Hinh 1. So do yeu cau BTTH05: thong tin ket noi duoc dua ra file cau hinh, provider tao connection cho sqlite/sqlserver/access/oracle/odbc, DataLayer gom logic query/non-query va cac DAO tai su dung lai lop dung chung. |
| `BTTH05_02_external_database_config.png` | Hinh 2. File database_config.ini luu provider va connection_string ben ngoai ma nguon, kem vi du cau hinh SQLite, SQL Server, Access va Oracle; config.py doc file nay de tao DB_SETTINGS cho tang du lieu. |
| `BTTH05_03_database_provider_factory.png` | Hinh 3. db_provider.py tao connection theo provider trong cau hinh: SQLite dung sqlite3, SQL Server/Access/Oracle/ODBC dung pyodbc va driver tuong ung, giup chuong trinh de doi DBMS. |
| `BTTH05_04_reusable_data_layer.png` | Hinh 4. DataLayer gom cac thao tac truy cap du lieu lap lai: execute_non_query cho them/sua/xoa, fetch_all/fetch_one cho truy van va scalar cho gia tri don. |
| `BTTH05_05_dao_reuse_datalayer.png` | Hinh 5. Cac DAO cu the da chuyen sang goi DataLayer cho insert, update, delete va query; service/UI van dung cac ham DAO cu nen khong lam thay doi nghiep vu hien co. |
| `BTTH05_06_runtime_data_access_check.png` | Hinh 6. Ket qua chay kiem tra: service van doc duoc du lieu hoc sinh, lop, giao vien va activity; DataLayer truy van truc tiep duoc bang HOCSINH. |
| `BTTH05_07_running_app_dashboard_after_datalayer.png` | Hinh 7. Phan mem HSMS chay duoc sau BTTH05; dashboard lay du lieu thong qua service/DAO da refactor sang DataLayer. |

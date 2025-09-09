# pipy_publish.py
- prepare/install package
    pip install setuptools wheel
    pip install twine

- update info, version, descriptions,... in [prod] setup.py or [dev] setup-dev.py
- create/get token publish pipy https://pypi.org/manage/account/token/
- run sh script publish pipy
    [prod] ./pipy_publish.sh setup.py
        prod token: create at https://pypi.org/manage/account/token/
    [dev]  ./pipy_publish.sh setup-dev.py
        dev token: pypi-AgEIcHlwaS5vcmcCJGQ2MzdhMjBiLTE3MjMtNGVjOC04NjI4LTBkMDc4NDM3ZTZlNgACKlszLCJmYmQzYjY2My0zYzBkLTQzMGItYTVjZi03OGExMjkxNmI5MzEiXQAABiBPQ_Y0NCkkoFXiqkGI57hzDca-ndEYk5LWMLjW7Ul6Dg

## Poetry install list packages
1. install poetry: curl -sSL https://install.python-poetry.org | python3 -
2. cd ~/root-directory/shared/nectarpy-publisher
3. run command:
    - poetry lock
    - poetry install
    - run py project
# 建立虛擬環境
uv venv

# 輸出requirements.txt
uv pip compile pyproject.toml -o requirements.txt


# 安裝建置相依
uv pip install -r requirements.txt

# 建立 wheel
uv run python -m build --wheel
python setup.py build_ext --inplace
python -m build --wheel

# 清理所有產物
python setup.py clean

# 檢查 wheel 內容
unzip -l dist/algo-0.1.0-*.whl
# ✅ algo/__init__.py
# ✅ algo/func01/func01.cpython-*.so
# ✅ algo/func02/func02.cpython-*.so
# ✅ algo-0.1.0.dist-info/*

# 安裝並測試
uv pip install dist/algo-0.1.0-*.whl

uv run python - <<'PY'
import algo
print("5! =", algo.factorial(5))
print("Fib(10) =", algo.fib(10))
PY



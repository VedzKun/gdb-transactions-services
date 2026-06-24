# Quick Database Setup Guide

## TL;DR - Just Run This

```bash
cd transactions_service

# Test connection
python test_connection.py

# Create database and tables
python setup_db.py
```

That's it! Both scripts now handle everything automatically.

---

## What Each Script Does

### 1. `test_connection.py` - Connection Verification
- Tests if PostgreSQL server is accessible
- Verifies password is correct
- Checks if database exists
- Shows helpful error messages

**Run first:**
```bash
python test_connection.py
```

**Expected output if everything is OK:**
```
✅ Can connect to 'postgres' database
✅ Can connect to 'gdb_transactions_db' database
🎉 All connections successful!
Next step: python setup_db.py
```

---

### 2. `setup_db.py` - Database & Tables Creation
- Creates the database (if it doesn't exist)
- Creates all 3 tables:
  - `fund_transfers`
  - `transaction_logs`
  - `transfer_limits`
- Adds indexes for performance
- Verifies everything was created

**Run after test_connection.py:**
```bash
python setup_db.py
```

**Expected output:**
```
✅ fund_transfers table created successfully
✅ transaction_logs table created successfully
✅ transfer_limits table created successfully
🎉 All tables created successfully!
```

---

## Configuration

Your `.env` file already has the correct settings:

```properties
DATABASE_URL=postgresql://postgres:anil@localhost:5432/gdb_transactions_db
```

The scripts automatically extract:
- **User:** postgres
- **Password:** anil
- **Host:** localhost
- **Port:** 5432
- **Database:** gdb_transactions_db

---

## Full Workflow

```bash
# 1. Make sure you're in transactions_service directory
cd transactions_service

# 2. Activate virtual environment (if not already)
.venv\Scripts\activate

# 3. Verify connection works
python test_connection.py
# Should show: ✅ All connections successful!

# 4. Create database and tables
python setup_db.py
# Should show: 🎉 All tables created successfully!

# 5. Start the application
uvicorn app.main:app --host 0.0.0.0 --port 8002

# 6. Check it's running
# Open browser: http://localhost:8002/api/docs
```

---

## If test_connection.py Fails

### Error: "❌ Cannot connect to PostgreSQL server"

**Solutions:**

1. **Start PostgreSQL service:**
   ```powershell
   # As Administrator
   net start PostgreSQL14
   ```

2. **Check PostgreSQL is installed:**
   ```powershell
   psql --version
   ```

3. **Verify in Services.msc:**
   - Press Windows + R
   - Type: `services.msc`
   - Find "PostgreSQL" service
   - Right-click → Start

### Error: "❌ INVALID PASSWORD"

The password `anil` might not be set for the `postgres` user.

**Solutions:**

1. **Using psql (if available):**
   ```bash
   psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'anil';"
   ```

2. **Using pgAdmin (GUI):**
   - Open pgAdmin from Start menu
   - Right-click postgres role
   - Properties → Definition → Set password to: `anil`
   - Save

3. **Reinstall PostgreSQL:**
   - Make sure to set postgres password to `anil` during installation

### Error: "❌ Database does not exist"

This is OK! Just run `python setup_db.py` and it will be created automatically.

---

## Verify Setup Worked

After running `setup_db.py`, verify:

```bash
# Check tables exist
psql -U postgres -h localhost -d gdb_transactions_db -c "\dt"

# Should show:
#            List of relations
#  Schema |        Name        | Type  |  Owner
# --------+--------------------+-------+----------
#  public | fund_transfers     | table | postgres
#  public | transaction_logs   | table | postgres
#  public | transfer_limits    | table | postgres
```

---

## Next Steps

After database is set up:

1. **Start the service:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8002
   ```

2. **Check health endpoint:**
   ```bash
   curl http://localhost:8002/health
   ```

3. **View API documentation:**
   ```
   http://localhost:8002/api/docs
   ```

4. **Try a test request:**
   ```bash
   curl -X POST http://localhost:8002/api/v1/deposits \
     -H "Content-Type: application/json" \
     -d '{"account_number": "ACC001", "amount": 100.00, "description": "Test"}'
   ```

---

## File Reference

| File | Purpose |
|------|---------|
| `test_connection.py` | Verify PostgreSQL connection works |
| `setup_db.py` | Create database and tables |
| `reset_db.py` | Reset database (delete all data) |
| `.env` | Configuration (passwords, URLs, etc.) |
| `POSTGRESQL_PASSWORD_FIX.md` | If you need to fix PostgreSQL password |
| `DB_SETUP_README.md` | Detailed documentation |

---

## Troubleshooting Checklist

- [ ] PostgreSQL service is running (`net start PostgreSQL14`)
- [ ] Password is set to `anil` for postgres user
- [ ] Host is `localhost` and port is `5432`
- [ ] .env file has correct DATABASE_URL
- [ ] Ran `python test_connection.py` and it passed
- [ ] Ran `python setup_db.py` and it completed
- [ ] Tables are visible in database

---

## Getting Tables Into Database

### Method 1: Automatic (Recommended)

```bash
python setup_db.py
```

The script will:
1. ✅ Create database if needed
2. ✅ Create all 3 tables
3. ✅ Add indexes
4. ✅ Verify everything

### Method 2: Manual (psql)

```bash
# Create database
psql -U postgres -c "CREATE DATABASE gdb_transactions_db;"

# Then run our script
python setup_db.py
```

### Method 3: Using pgAdmin

1. Open pgAdmin
2. Right-click Databases → Create → Database
3. Name: `gdb_transactions_db`
4. Save
5. Run: `python setup_db.py`

---

## If Everything Fails

**Nuclear option - Fresh PostgreSQL Install:**

```bash
# 1. Uninstall PostgreSQL completely
#    Control Panel > Programs > Uninstall a Program
#    Find "PostgreSQL" and uninstall

# 2. Download fresh copy
#    https://www.postgresql.org/download/windows/

# 3. Install with these settings:
#    - Installation Directory: C:\Program Files\PostgreSQL\14
#    - postgres password: anil (IMPORTANT!)
#    - Port: 5432
#    - Locale: default

# 4. Verify
psql --version

# 5. Test connection
python test_connection.py

# 6. Create database
python setup_db.py
```

---

**Status:** ✅ Ready to use
**Last Updated:** 2025-12-24

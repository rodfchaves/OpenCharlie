REPO_URL="https://github.com/rodfchaves/OpenCharlie.git"
LOCAL_DIR="OpenCharlie"
DB_NAME="gmcharlie"

git clone $REPO_URL $LOCAL_DIR

cd $LOCAL_DIR

python -m venv venv
source venv/bin/activate

pip install --no-cache-dir -r requirements.txt

createdb gmcharlie
psql -d gmcharlie -f default.sql

python app.py
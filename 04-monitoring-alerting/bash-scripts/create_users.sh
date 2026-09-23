#!/bin/bash

COUNTER_FILE="/var/lib/create-users/counter"

# Root ekanligini tekshirish
if [[ $EUID -ne 0 ]]; then
    echo "XATO: Script root yoki sudo orqali ishga tushirilishi kerak."
    exit 1
fi

# Counter uchun papka yaratish
mkdir -p "$(dirname "$COUNTER_FILE")"

# Counter mavjud bo'lmasa 1 dan boshlash
if [[ ! -f "$COUNTER_FILE" ]]; then
    echo "1" > "$COUNTER_FILE"
fi

# Hozirgi password raqamini olish
COUNTER=$(cat "$COUNTER_FILE")

echo
echo "================================"
echo "      USER CREATION SCRIPT"
echo "================================"
echo

# Userlar sonini so'rash
read -rp "Nechta user yaratasiz: " USER_COUNT

# Son ekanligini tekshirish
if ! [[ "$USER_COUNT" =~ ^[0-9]+$ ]]; then
    echo "XATO: Userlar soni raqam bo'lishi kerak."
    exit 1
fi

if [[ "$USER_COUNT" -lt 1 ]]; then
    echo "XATO: Kamida 1 ta user yarating."
    exit 1
fi

echo
echo "User nomlarini bo'sh joy bilan kiriting."
echo "Masalan: ali vali sardor"
echo

read -rp "User nomlari: " -a USERS

# Userlar sonini tekshirish
if [[ "${#USERS[@]}" -ne "$USER_COUNT" ]]; then
    echo
    echo "XATO: Siz $USER_COUNT ta user yaratishni"
    echo "so'radingiz, lekin ${#USERS[@]} ta user kiritdingiz."
    exit 1
fi

echo
echo "================================"
echo "       NATIJA"
echo "================================"
echo

# Userlarni yaratish
for USER in "${USERS[@]}"
do

    # Username formatini tekshirish
    if ! [[ "$USER" =~ ^[a-z_][a-z0-9_-]*$ ]]; then
        echo "XATO: '$USER' noto'g'ri username."
        echo
        continue
    fi

    # User mavjudligini tekshirish
    if id "$USER" &>/dev/null; then
        echo "XATO: '$USER' useri allaqachon mavjud."
        echo
        continue
    fi

    # Password yaratish
    PASSWORD="devops@$COUNTER"

    # User yaratish
    useradd \
        -m \
        -s /bin/bash \
        "$USER"

    # Password berish
    echo "$USER:$PASSWORD" | chpasswd

    echo "User     : $USER"
    echo "Password : $PASSWORD"
    echo "Home     : /home/$USER"
    echo "Shell    : /bin/bash"
    echo "--------------------------------"

    # Keyingi password raqamiga o'tish
    ((COUNTER++))

done

# Counterni saqlash
echo "$COUNTER" > "$COUNTER_FILE"

echo
echo "================================"
echo "User yaratish tugadi."
echo "Keyingi password raqami: $COUNTER"
echo "================================"

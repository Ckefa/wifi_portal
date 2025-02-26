#!/bin/bash

# Database credentials and host details
DB_HOST="172.19.0.2"
DB_USER="admin"
DB_PASS="Admin1234"
DB_NAME="wifi"

usage() {
    echo "Usage:"
    echo "  $0 -table                  => Get all Users details"
    echo "  $0 -update                 => Updates Users table expiry for manually added users"
    echo "  $0 -total                  => Gets Total wifi revenue"
    echo "  $0 -add PHONE HOURS AMOUNT => Manully add user to table"
    echo "  $0 -get PHONE              => Get user details by phone"
    echo "  $0 -delete PHONE           => Delete User by phone"
    exit 1
}

if [ "$#" -lt 1 ]; then
    usage
fi

command="$1"

case "$command" in
    -table)
        # Display the users table
        mariadb -h ${DB_HOST} -u ${DB_USER} -p${DB_PASS} -e "SELECT * FROM ${DB_NAME}.users;"
        ;;
    -add)
        # Ensure phone, hours, and amount arguments are provided
        if [ "$#" -ne 4 ]; then
            usage
        fi

        PHONE="$2"
        HOUR="$3"
        AMOUNT="$4"

        # Validate that HOURS is a positive integer
        if ! [[ "$HOUR" =~ ^[1-9][0-9]*$ ]]; then
            echo "Error: HOURS must be a positive integer."
            exit 1
        fi

        # SQL statement to insert or update user
        SQL="INSERT INTO ${DB_NAME}.users (id, phone, package, amount, status, expiry, total)
        VALUES (UUID(), '${PHONE}', '${HOUR} Hour Package', ${AMOUNT}, 'active', DATE_ADD(NOW(), INTERVAL ${HOUR} HOUR), ${AMOUNT})
        ON DUPLICATE KEY UPDATE 
            expiry = DATE_ADD(expiry, INTERVAL ${HOUR} HOUR),
            package = '${HOUR} Hour Package',
            amount = ${AMOUNT},
            status = 'active',
            total = total + ${AMOUNT};"

        mariadb -h ${DB_HOST} -u ${DB_USER} -p${DB_PASS} -e "${SQL}"
        if [ $? -eq 0 ]; then
            echo "User with phone ${PHONE} added/updated successfully with ${HOUR} hour(s)."
        else
            echo "Failed to add/update user with phone ${PHONE}."
        fi
        ;;

       -get)
        # Ensure phone argument is provided
        if [ "$#" -ne 2 ]; then
            usage
        fi
        PHONE="$2"
        # Build SQL to retrieve user details
        SQL="SELECT * FROM ${DB_NAME}.users WHERE phone = '${PHONE}';"
        mariadb -h ${DB_HOST} -u ${DB_USER} -p${DB_PASS} -e "${SQL}"
        ;;

  -total)
        # SQL to sum the total column
        SQL="SELECT SUM(total) AS REVENUE FROM ${DB_NAME}.users;"

        mariadb -h ${DB_HOST} -u ${DB_USER} -p${DB_PASS} -e "${SQL}"
        if [ $? -eq 0 ]; then
            echo "Total sum calculated successfully."
        else
            echo "Failed to calculate total sum."
        fi
        ;;

  -update)
        # SQL to update users whose expiry has passed
        SQL="UPDATE ${DB_NAME}.users
             SET status = 'expired'
             WHERE expiry <= NOW() AND status != 'expired';"

        mariadb -h ${DB_HOST} -u ${DB_USER} -p${DB_PASS} -e "${SQL}"
        if [ $? -eq 0 ]; then
            echo "Expired users updated successfully."
        else
            echo "Failed to update expired users."
        fi

        # SQL to delete users where package is NULL
        SQL="DELETE FROM ${DB_NAME}.users WHERE package IS NULL;"

        mariadb -h ${DB_HOST} -u ${DB_USER} -p${DB_PASS} -e "${SQL}"
        if [ $? -eq 0 ]; then
            echo "Users with NULL package deleted successfully."
        else
            echo "Failed to delete users with NULL package."
        fi
        ;;
 
    -delete)
        # Ensure phone argument is provided
        if [ "$#" -ne 2 ]; then
            usage
        fi
        PHONE="$2"
        # Build SQL to delete user
        SQL="DELETE FROM ${DB_NAME}.users WHERE phone = '${PHONE}';"
        mariadb -h ${DB_HOST} -u ${DB_USER} -p${DB_PASS} -e "${SQL}"
        if [ $? -eq 0 ]; then
            echo "User with phone ${PHONE} deleted successfully."
        else
            echo "Failed to delete user with phone ${PHONE}."
        fi
        ;;
    *)
        usage
        ;;
esac

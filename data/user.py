from datetime import datetime


class User:
    # Check user subscription
    @staticmethod
    def check_status(phone: str) -> bool:
        print("Checking Status")

        try:
            with open("data/users.txt", "r") as file:
                for line in file:
                    # Each line is expected to be in the format: [phone package amount expirydatetime]
                    data = line.strip().split()
                    if len(data) < 6:
                        continue

                    file_phone, package, _, _, amount, expiry_datetime_str = data

                    print(
                        f"<<<<<<<<<< Fond {file_phone} {package} {amount} {expiry_datetime_str} >>>>>>"
                    )

                    # Check if the phone number matches
                    if file_phone == phone:
                        # Parse the expiry date (including microseconds)
                        expiry_datetime = datetime.strptime(
                            expiry_datetime_str, "%Y-%m-%dT%H:%M:%S.%f"
                        )

                        current_datetime = datetime.now()

                        # Return True if subscription is still active, else False
                        return current_datetime < expiry_datetime

            # If phone not found in file, return False
            return False

        except FileNotFoundError:
            print("The file 'users.txt' was not found.")
            return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False


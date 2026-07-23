import qnexus as qnx
print("Starting login process...")
qnx.login()
print("Login completed. Fetching devices...")
df = qnx.devices.get_all().df()
print(df)

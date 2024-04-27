from libs.ServerAPI.ServerAPI import ServerAPI
import getmac


def main():
    server_api = ServerAPI()
    print("next step")
    respond = server_api.new_agent_request(getmac.get_mac_address())
    print(respond)

if __name__ == '__main__':
    main()
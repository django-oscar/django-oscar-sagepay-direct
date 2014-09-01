# Fixtures
MALFORMED= "VPSProtocol=3.00\r\nStatus=MALFORMED\r\nStatusDetail=3009 : The VendorTxCode is missing."
INVALID = "VPSProtocol=2.23\r\nStatus=INVALID\r\nStatusDetail=The IP address of the server sending the transaction does not match the valid IP address ranges listed in the Simulator.  The IP address Simulator sees for your server is 46.208.58.187.  You can add this IP in the Accounts section of Simulator if you wish."
OK = 'VPSProtocol=2.23\r\nStatus=OK\r\nStatusDetail=Direct transaction from Simulator.\r\nVPSTxId={0E86E19A-4B7B-476A-ADEB-60E8A13F75A9}\r\nSecurityKey=LPGESWTU38\r\nTxAuthNo=4752\r\nAVSCV2=DATA NOT CHECKED\r\nAddressResult=NOTCHECKED\r\nPostCodeResult=NOTCHECKED\r\nCV2Result=NOTCHECKED\r\n'
REGISTERED = 'VPSProtocol=2.23\r\nStatus=REGISTERED\r\nStatusDetail=Direct transaction from Simulator.\r\nVPSTxId={F4CC513C-9436-4E88-AEB2-B9DFEF52FF00}\r\nSecurityKey=3U9BZE03UL\r\n'

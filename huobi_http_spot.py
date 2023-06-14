"""
    火币httpClient
"""
import requests
from datetime import datetime
from enum import Enum
import hmac
import hashlib
import base64
from urllib.parse import urlencode, quote
import json
from requests import Response
from config import config
#from threading import Lock

class HuobiPeriod(Enum):
    MINUTE_1 = "1min"
    MINUTE_5 = "5min"
    MINUTE_15 = "15min"
    MINUTE_30 = "30min"
    HOUR_1 = "60min"
    DAY_1 = "1day"
    WEEK_1 = "1week"
    YEAR_1 = "1year"

class RequestMethod(Enum):
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    PUT = "PUT"

class HuobiHttpSpot(object):
    """
    火币http client 公开和签名的接口.
    """

    def __init__(self, host=None, key=None, secret=None, timeout=5):
        self.host = host if host else "https://api.huobi.pro"   # https://api.huobi.br.com # https://api.huobi.co
        self.api_host = 'api.huobi.pro'  # api.huobi.br.com
        self.key = key
        self.secret = secret
        self.timeout = timeout
        #self.lock  = Lock()

    def _request(self, method: RequestMethod, path, params=None, body=None, verify=False):

        url = self.host + path
        if params and not verify:
            url = url + '?' + self._build_params(params)

        if verify:
            sign_data = self._sign(method.value, path, params)
            url = url + '?' + self._build_params(sign_data)
        headers = {"Content-Type": "application/json"}

        # print(url)
        if body:
            data = json.dumps(body)
            try:
                response: Response = requests.request(method.value, url, headers=headers, params=params, data=data, timeout=self.timeout)
            except:
                print("no response")
                return 0

        else:
            try:
                response: Response = requests.request(method.value, url, headers=headers, params=params, timeout=self.timeout)
            except:
                print("no response")
                return 0

        json_data = response.json()

        if response.status_code == 200 and json_data['status'] == 'ok':
            return json_data['data']
        else:
            print(json_data)
            return 0
            #print(json_data)
            #raise Exception(f"请求{url}的数据发生了错误：{json_data}")

    def get_time_stamp(self):
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

    def _build_params(self, params: dict):
        """
        构造query string
        :param params:
        :return:
        """
        return '&'.join([f"{key}={params[key]}" for key in params.keys()])

    def get_symbols(self):
        """
        此接口返回所有火币全球站支持的交易对。
        :return:
        """
        path = "/v1/common/symbols"

        #url = self.host + path
        #json_data = requests.get(url, timeout=self.timeout).json()
        # if json_data['status'] == 'ok':
        #     return json_data['data']
        #
        # raise Exception(f"请求{url}的数据发生错误, 错误信息--> {json_data}")

        return self._request(RequestMethod.GET, path)

    def get_currencys(self):
        """
        此接口返回所有火币全球站支持的币种。
        :return:
        """
        path = "/v1/common/currencys"
        # url = self.host + path
        # json_data = requests.get(url, timeout=self.timeout).json()
        # if json_data['status'] == 'ok':
        #     return json_data['data']
        #
        # raise Exception(f"请求{url}的数据发生错误, 错误信息--> {json_data}")

        return self._request(RequestMethod.GET, path)

    def get_exchange_timestamp(self):

        path = "/v1/common/timestamp"
        # url = self.host + path
        # json_data = requests.get(url, timeout=self.timeout).json()
        # if json_data['status'] == 'ok':
        #     return json_data['data']
        #
        # raise Exception(f"请求{url}的数据发生错误, 错误信息--> {json_data}")

        return self._request(RequestMethod.GET, path)

    def get_kline_data(self, symbol: str, period:str, size=2000):
        path = "/market/history/kline"
        params = {"symbol": symbol, "period": period, "size": size}

        # url = self.host + path
        # url = url + '?' + self._build_params(params)
        # print(url)
        # exit()
        # json_data = requests.get(url, params=params, timeout=self.timeout).json()
        # # json_data = requests.get(url, timeout=self.timeout).json()
        # if json_data['status'] == 'ok':
        #     return json_data['data']
        #
        # raise Exception(f"请求{url}的数据发生错误, 错误信息--> {json_data}")

        # 优化后的代码.
        return self._request(RequestMethod.GET, path, params=params)

    def get_tickers(self):
        path = "/market/tickers"

        url = self.host + path
        json_data = requests.get(url, timeout=self.timeout).json()
        if json_data['status'] == 'ok':
            return json_data['data']

        # return json_data
        raise Exception(f"请求{url}的数据发生错误, 错误信息--> {json_data}")

        # return self._request(RequestMethod.GET, path)

    def get_ticker(self, symbol=None, depth=5, type='step0'):
        """
        :param symbol: btcusdt  orderbook
        :param depth: value should be: 5 10  20
        :param type: step0 step1 step2 step3 step 4 step5
        :return: 返回ticker数据
        """

        path = "/market/depth"
        url = self.host + path
        params = {"symbol": symbol, 'depth': depth, "type": type}
        json_data = requests.get(url, params=params, timeout=self.timeout).json()
        # print(json_data)
        if json_data['status'] == 'ok':
            return json_data['tick']
        raise Exception(f"请求{url}的数据发生错误, 错误信息--> {json_data}")

        # return self._request(RequestMethod.GET, path, params=params)
    def get_all_ticker(self):
        path = '/market/tickers'
        url = self.host + path
        json_data = requests.get(url,  timeout=self.timeout).json()
        if json_data['status'] == 'ok':
            return json_data['data']
        raise Exception(f"请求{url}的数据发生错误, 错误信息--> {json_data}")

    def get_market_detail(self, symbol):
        path = "/market/detail"
        url = self.host + path
        params = {"symbol": symbol}
        json_data = requests.get(url, params=params, timeout=self.timeout).json()
        if json_data['status'] == 'ok':
            return json_data['tick']
        raise Exception(f"请求{url}的数据发生错误, 错误信息--> {json_data}")

        # return self._request(RequestMethod.GET, path, params=params)

    def place_merged_order(self, account_id, symbols, type, amount, price=None, source='spot-api', stop_price=None, operator=None):
        """

        :param account_id: 账户 ID，使用 GET /v1/account/accounts 接口查询。现货交易使用 ‘spot’ 账户的 account-id；杠杆交易，请使用 ‘margin’ 账户的 account-id
        :param symbol: 交易对, 例如btcusdt, ethbtc
        :param type: 订单类型，包括buy-market, sell-market, buy-limit, sell-limit, buy-ioc, sell-ioc, buy-limit-maker, sell-limit-maker（说明见下文）, buy-stop-limit, sell-stop-limit
        :param amount: 订单交易量（市价买单此字段为订单交易额）
        :param price: limit order的交易价格
        :param source: 止盈止损订单触发价格
        :param stop_price: 止盈止损订单触发价格
        :param operator: 止盈止损订单触发价运算符 gte – greater than and equal (>=), lte – less than and equal (<=)
        :return:
        """
        path = "/v1/order/batch-orders"
        body = []
        for symbol in symbols:
            order = {'account-id': account_id,
                    'symbol': symbol,
                    'type':  type,
                    'amount': amount,
                    'source': source
                }
            if price:
                order['price'] = str(price)

            if stop_price:
                order['stop-price'] = str(stop_price)

            if operator:
                order['operator'] = operator

            body.append(order)
        sign_data = self._sign('POST', path)

        url = self.host + path + '?' + self._build_params(sign_data)


        headers = {"Content-Type": "application/json"}
        json_data = requests.post(url, headers=headers, data=json.dumps(body), timeout=self.timeout).json()
        if json_data['status'] == 'ok':
            print(f"Create batch order: {symbols}, amount:{float(amount)*5}, type: {type}")
            #return json_data['data']
            return 1
        else:
            return 0
            raise Exception(f"请求{url}发生错误...{json_data}")


    ######################## private data ###################


    def _sign(self, method, path, params=None):

        """
        该方法为签名的方法
        :return:
        """
        sorted_params = [
            ("AccessKeyId", self.key),
            ("SignatureMethod", "HmacSHA256"),
            ("SignatureVersion", "2"),
            ("Timestamp", datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"))
        ]

        if params:
            sorted_params.extend(list(params.items()))
            sorted_params = list(sorted(sorted_params))

        encode_params = urlencode(sorted_params)

        payload = [method, self.api_host, path, encode_params]
        payload = "\n".join(payload)
        payload = payload.encode(encoding="UTF8")
        secret_key = self.secret.encode(encoding="UTF8")
        digest = hmac.new(secret_key, payload, digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(digest).decode("UTF8")
        sign_params = dict(sorted_params)  # header key  # 路径。
        sign_params["Signature"] = quote(signature) # uri
        return sign_params

    def get_accounts(self):

        """
        获取账户信息的方法.
         [{'id': 897261, 'type': 'spot', 'subtype': '', 'state': 'working'},
         {'id': 6703531, 'type': 'margin', 'subtype': 'adausdt', 'state': 'working'},
          {'id': 7070883, 'type': 'margin', 'subtype': 'bsvusdt', 'state': 'working'},
          {'id': 5157717, 'type': 'margin', 'subtype': 'btmusdt', 'state': 'working'},
          {'id': 7471276, 'type': 'margin', 'subtype': 'ethusdt', 'state': 'working'},
          {'id': 5153600, 'type': 'margin', 'subtype': 'ontusdt', 'state': 'working'},
          {'id': 6290114, 'type': 'margin', 'subtype': 'xrpusdt', 'state': 'working'},
          {'id': 3214863, 'type': 'otc', 'subtype': '', 'state': 'working'},
          {'id': 3360132, 'type': 'point', 'subtype': '', 'state': 'working'}]
        :return:
        """

        path = "/v1/account/accounts"

        sign_data = self._sign('GET', path)
        url = self.host + path
        url += '?' + self._build_params(sign_data)
        # print(url)
        # exit()
        json_data = requests.get(url,  timeout=self.timeout).json()
        # json_data = requests.get(url, timeout=self.timeout).json()
        if json_data['status'] == 'ok':
            return json_data['data']

        raise Exception(f"请求{url}的数据发生错误, 错误信息--> {json_data}")

        # return self._request(RequestMethod.GET, path, verify=True)

    #def get_account_accounts(self):
    #    path = '/v1/account/accounts'


    def get_account_balance(self, account_id):
        """
        查询指定账户的余额，支持以下账户：
        spot：现货账户， margin：杠杆账户，otc：OTC 账户，point：点卡账户
        :param account_id:
        :return:
        """
        path = f'/v1/account/accounts/{account_id}/balance'
        #print(path)
        # exit()
        url = self.host + path
        sign_data = self._sign('GET', path)
        # print(sign_data)
        url += '?' + self._build_params(sign_data)
        #print(url)
        # exit()
        json_data = requests.get(url, timeout=self.timeout).json()
        if json_data['status'] == 'ok':
            return json_data['data']
        raise Exception(f"请求{url}的数据发生错误, 错误信息--> {json_data}")



    def place_order(self, account_id, symbol, type, amount, price=None, source='api', stop_price=None, operator=None):
        """
        #,
        :param account_id: 账户 ID，使用 GET /v1/account/accounts 接口查询。现货交易使用 ‘spot’ 账户的 account-id；杠杆交易，请使用 ‘margin’ 账户的 account-id
        :param symbol: 交易对, 例如btcusdt, ethbtc
        :param type: 订单类型，包括buy-market, sell-market, buy-limit, sell-limit, buy-ioc, sell-ioc, buy-limit-maker, sell-limit-maker（说明见下文）, buy-stop-limit, sell-stop-limit
        :param amount: 订单交易量（市价买单此字段为订单交易额）
        :param price: limit order的交易价格
        :param source: 止盈止损订单触发价格
        :param stop_price: 止盈止损订单触发价格
        :param operator: 止盈止损订单触发价运算符 gte – greater than and equal (>=), lte – less than and equal (<=)
        :return:
        """
        path = "/v1/order/orders/place"

        body = {'account-id': account_id,
                'symbol': symbol,
                'type':  type,
                'amount': str(amount),
                'source': source
                }

        if price:
            body['price'] = str(price)

        if stop_price:
            body['stop-price'] = str(stop_price)

        if operator:
            body['operator'] = operator

        sign_data = self._sign('POST', path)

        url = self.host + path + '?' + self._build_params(sign_data)


        headers = {"Content-Type": "application/json"}
        try:
            json_data = requests.post(url, headers=headers, data=json.dumps(body), timeout=self.timeout).json()
            if json_data['status'] == 'ok':
                print(f"Create spot order: {symbol}, amount:{amount}, type: {type}")
                return 1
            else:
                raise Exception(f"请求{url}发生错误...{json_data}")
                return 0
        except:
            return 0

        # return self._request(RequestMethod.POST, path, body=body, verify=True)

    def place_trigger_order(self, accountId, symbol, orderSide, orderType, clientOrderId, stopPrice, orderPrice=None, orderSize = None, orderValue=None,  timeInForce = None ):
        """

        :param account_id: 账户 ID，使用 GET /v1/account/accounts 接口查询。现货交易使用 ‘spot’ 账户的 account-id；杠杆交易，请使用 ‘margin’ 账户的 account-id
        :param symbol: 交易对, 例如btcusdt, ethbtc
        :param type: 订单类型，包括buy-market, sell-market, buy-limit, sell-limit, buy-ioc, sell-ioc, buy-limit-maker, sell-limit-maker（说明见下文）, buy-stop-limit, sell-stop-limit
        :param amount: 订单交易量（市价买单此字段为订单交易额）
        :param price: limit order的交易价格
        :param source: 止盈止损订单触发价格
        :param stop_price: 止盈止损订单触发价格
        :param operator: 止盈止损订单触发价运算符 gte – greater than and equal (>=), lte – less than and equal (<=)
        :return:
        """
        path = "/v2/algo-orders"

        body = {'accountId': accountId,
                'symbol': symbol,
                'orderSide':  orderSide,
                'orderType': orderType,
                'clientOrderId': clientOrderId,
                'stopPrice': str(stopPrice)
                }

        if orderSize:
            #print("yes")
            body['orderSize'] = str(orderSize)

        if orderPrice:
            body['orderPrice'] = str(orderPrice)

        if orderValue:
            body['orderValue'] = str(orderValue)

        if timeInForce:
            body['timeInForce'] = str(timeInForce)

        sign_data = self._sign('POST', path)

        url = self.host + path + '?' + self._build_params(sign_data)
        print(body)

        headers = {"Content-Type": "application/json"}
        json_data = requests.post(url, headers=headers, data=json.dumps(body), timeout=self.timeout).json()
        print(json_data)
        if json_data['code'] == 200:
            print(f"Create trigger order: {symbol}, orderType: {orderType}")
            #return json_data['data']
            return json_data
        raise Exception(f"请求{url}发生错误...{json_data}")

        # return self._request(RequestMethod.POST, path, body=body, verify=True)





    def cancel_order(self, order_id):
        path = f'/v1/order/orders/{order_id}/submitcancel'

        url = self.host + path
        sign_data = self._sign('POST', path)
        url += '?' + self._build_params(sign_data)
        headers = {"Content-Type": "application/json"}
        json_data = requests.post(url, headers=headers, timeout=self.timeout).json()
        print(json_data)
        if json_data['status'] == 'ok':
            return json_data['data']
        else:
            return json_data

        # return self._request(RequestMethod.POST, path, verify=True)

    def get_open_orders(self, account_id, symbol, side=None, from_=None, direct=None, size=100):
        """

        :param account_id:
        :param symbol:
        :param side:
        :param from_: 查询起始 ID
        :param direct: 如字段'from'已设定，此字段'direct'为必填) 查询方向 (prev - 以起始ID升序检索；next - 以起始ID降序检索)
        :param size:
        :return:
        """

        path = '/v1/order/openOrders'
        params = {'account-id': account_id,
                  "symbol": symbol,
                  "size": size}
        if side:
            params["side"] = side

        if from_ and direct:
            params['from'] = from_
            params['direct'] = direct


        sign_data = self._sign('GET', path, params=params)

        url = self.host + path + '?' + self._build_params(sign_data)
        # print(url)
        # exit()
        json_data = requests.get(url, timeout=self.timeout).json()
        if json_data['status'] == 'ok':
            return json_data['data']
        raise Exception(f'请求{url}发生错误..{json_data}')

        # return self._request(RequestMethod.GET, path, params=params, verify=True)



    def cancel_orders(self, account_id, symbol=None, side=None, size=None):
        path = "/v1/order/orders/batchCancelOpenOrders"

        body = {'account-id': account_id}

        if symbol:
            body['symbol'] = symbol

        if side:
            body['side'] = side

        if size:
            body['size'] = size

        url = self.host + path

        sign_data = self._sign('POST', path)
        url += '?' + self._build_params(sign_data)
        headers = {"Content-Type": "application/json"}
        json_data = requests.post(url, headers=headers, data=json.dumps(body), timeout=self.timeout).json()
        if json_data['status'] == 'ok':
            return json_data['data']
        else:
            return json_data
        raise Exception(f"请求{url}的数据发生错误, 错误信息--> {json_data}")

        # return self._request(RequestMethod.POST, path, body=body, verify=True)

    def cancel_orders_by_ids(self, ids:list):
        path = '/v1/order/orders/batchcancel'
        body = {'order-ids': ids}

        url = self.host + path
        sign_data = self._sign('POST', path)
        url += '?' + self._build_params(sign_data)
        headers = {"Content-Type": "application/json"}
        json_data = requests.post(url, headers=headers, data=json.dumps(body), timeout=self.timeout).json()
        print(json_data)
        if json_data['status'] == 'ok':
            return json_data['data']
        else:
            return json_data

        # return self._request(RequestMethod.POST, path, body=body, verify=True)

    def get_order_details(self, order_id):
        path = f'/v1/order/orders/{order_id}'

        sign_data = self._sign('GET', path)
        url = self.host + path + '?' + self._build_params(sign_data)

        json_data = requests.get(url, timeout=self.timeout).json()
        print(json_data)
        if json_data['status'] == 'ok':
            return json_data['data']

        raise Exception(f'请求{url}发生错误..{json_data}')

    def spot_contract_transfer(self, from_, to_, currency, amount, margin_account = None):
        path = "/v2/account/transfer"
        url = self.host + path

        body = {'from': from_, 'to': to_, 'currency': currency, 'amount': amount}
        if margin_account:
            body['margin-account'] = margin_account
        sign_data = self._sign('POST', path)
        url += '?' + self._build_params(sign_data)
        headers = {"Content-Type": "application/json"}

        json_data = requests.post(url, headers=headers, data=json.dumps(body), timeout=self.timeout).json()
        #print(json_data)
        if json_data['code'] == 200:
            return 1
            #return(json_data)
        else:
            print('error in transfering')

            raise Exception(f"请求{url}的数据发生错误, 错误信息--> {json_data}")
            return 0



    def get_loan_info(self, symbol=None):
        path = '/v1/margin/loan-info'
        #url = self.host +path
        if symbol:
            params = {'symbols': symbol}
            sign_data = self._sign('GET', path, params=params)
        else:
            sign_data = self._sign('GET', path)
        url = self.host + path + '?' + self._build_params(sign_data)

        try:
            json_data = requests.get(url, timeout=self.timeout).json()
        except:
            print("no response")
            return 0

        if json_data['status'] == 'ok':
            return json_data['data']
        else:
            return 0
            print(json_data)


    def spot_margin_transfer(self, symbol, currency, amount, direction):
        if direction == 'SPOTMARGIN':
            path = '/v1/dw/transfer-in/margin'
        elif direction == 'MARGINSPOT':
            path = '/v1/dw/transfer-out/margin'

        body = {'symbol': symbol, 'currency': currency, 'amount': amount}
        #print(body)
        url = self.host + path
        sign_data = self._sign('POST', path)
        url += '?' + self._build_params(sign_data)
        headers = {"Content-Type": "application/json"}
        try:
            json_data = requests.post(url, headers=headers, data=json.dumps(body), timeout=self.timeout).json()
            #print(json_data)
            if json_data['status'] == 'ok':
                return json_data['data']
            else:
                #return json_data
                print(json_data)
                return 0
        except:
            return 0
            print("no response")

    def get_loanable_amt(self, symbol):
        info = self.get_loan_info(symbol)
        if info == 0:
            return info
        else:
            #print(info)
            return info[0]['currencies'][0]['min-loan-amt'], info[0]['currencies'][0]['loanable-amt'], info[0]['currencies'][0]['max-loan-amt']

    def borrow_coin_order(self, symbol, currency, amt):
        path = '/v1/margin/orders'
        body = {'symbol': symbol, 'currency': currency, 'amount':amt}
        url = self.host + path
        sign_data = self._sign('POST', path)
        url += '?' + self._build_params(sign_data)
        headers = {"Content-Type": "application/json"}
        try:
            json_data = requests.post(url, headers=headers, data=json.dumps(body), timeout=self.timeout).json()

            if json_data['status'] == 'ok':
                print(f"success in borrwing {amt} {currency}")
                return json_data['data']
            else:
                print("error in borrwing coin")
                return 0
        except:
            print("no response in borrwing coin")
            return 0

    def get_loan_orders(self, symbol):
        path = '/v1/margin/loan-orders'

        sign_data = self._sign('GET', path)
        url = self.host + path + '?' + self._build_params(sign_data)

        json_data = requests.get(url, timeout=self.timeout).json()

        if json_data['status'] == 'ok':
            return json_data['data']

    def repay_loan(self, order_id, amt):
        path = f'/v1/margin/orders/{order_id}/repay'
        body = {'amount': amt}
        url = self.host + path
        sign_data = self._sign('POST', path)
        url += '?' + self._build_params(sign_data)
        headers = {"Content-Type": "application/json"}
        json_data = requests.post(url, headers=headers, data=json.dumps(body), timeout=self.timeout).json()
        #print(json_data)
        if json_data['status'] == 'ok':
            return json_data['data']
        else:
            return json_data

    def get_loan_account_info(self, symbol=None):
        path = '/v1/margin/accounts/balance'
        # url = self.host +path
        if symbol:
            params = {'symbol': symbol}
            sign_data = self._sign('GET', path, params=params)
        else:
            sign_data = self._sign('GET', path)
        url = self.host + path + '?' + self._build_params(sign_data)

        json_data = requests.get(url, timeout=self.timeout).json()
        #print(json_data)
        if json_data['status'] == 'ok':
            return json_data['data']







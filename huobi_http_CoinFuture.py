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

class HuobiHttpCoinFuture(object):
    """
    火币http client 公开和签名的接口.
    """

    def __init__(self, host=None, key=None, secret=None, timeout=5):
        self.host = host if host else "https://api.hbdm.com"   # https://api.huobi.br.com # https://api.huobi.co
        self.api_host = 'api.hbdm.com'  # api.huobi.br.com
        self.key = key
        self.secret = secret
        self.timeout = timeout

    def _request(self, method: RequestMethod, path, params=None, body=None, verify=False):

        url = self.host + path
        #if params and not verify:
        #    url = url + '?' + self._build_params(params)

        if verify:
            sign_data = self._sign(method.value, path, params)
            url = url + '?' + self._build_params(sign_data)
        headers = {"Content-Type": "application/json"}

        # print(url)
        if method.value == 'POST':
            data = json.dumps(body)
        #print(url)#
            response : Response= requests.request(method.value, url, headers=headers, params=params, data=data, timeout=self.timeout)
        elif method.value == 'GET':
            response: Response = requests.request(method.value, url, headers=headers, params=params,
                                                  timeout=self.timeout)
        #print(response)
        json_data = response.json()
        #print(json_data)
        #"""
        if response.status_code == 200 and json_data['status'] == 'ok':
            return json_data
        else:
            return 0
            #raise Exception(f"请求{url}的数据发生了错误：{json_data}")
        #"""


    def _build_params(self, params: dict):
        """
        构造query string
        :param params:
        :return:
        """
        return '&'.join([f"{key}={params[key]}" for key in params.keys()])

    def get_contract_info(self, symbol=None):
        """
        此接口返回所有火币全球站支持的交易对。
        :return:
        """
        path = "/swap-api/v1/swap_contract_info"
        if symbol:
            params = {"contract_code": symbol}
            return self._request(RequestMethod.GET, path, params=params)
        else:
            return self._request(RequestMethod.GET, path)
        # url = self.host + path
        # json_data = requests.get(url, timeout=self.timeout).json()
        # if json_data['status'] == 'ok':
        #     return json_data['data']
        #
        # raise Exception(f"请求{url}的数据发生错误, 错误信息--> {json_data}")


    def get_swap_index(self, symbol=None):
        """
        此接口返回所有火币全球站支持的交易对。
        :return:
        """
        path = "/swap-api/v1/swap_index"
        if symbol:
            params = {"contract_code": symbol}
            return self._request(RequestMethod.GET, path, params=params)
        else:
            return self._request(RequestMethod.GET, path)

    def get_tick_data(self, contract_code, step):
        """
        此接口返回所有火币全球站支持的交易对。
        :return:
        """
        path = "/swap-ex/market/depth"
        params = {'contract_code': contract_code, "type": step}
        # url = self.host + path,
        # json_data = requests.get(url, timeout=self.timeout).json()
        # if json_data['status'] == 'ok':
        #     return json_data['data']
        #
        # raise Exception(f"请求{url}的数据发生错误, 错误信息--> {json_data}")

        return self._request(RequestMethod.GET, path, params=params)['tick']

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

        path = "/api/v1/timestamp"
        # url = self.host + path
        # json_data = requests.get(url, timeout=self.timeout).json()
        # if json_data['status'] == 'ok':
        #     return json_data['data']
        #
        # raise Exception(f"请求{url}的数据发生错误, 错误信息--> {json_data}")

        return self._request(RequestMethod.GET, path)


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

    def get_market_detail(self, symbol):
        path = "/market/detail"
        url = self.host + path
        params = {"symbol": symbol}
        json_data = requests.get(url, params=params, timeout=self.timeout).json()
        if json_data['status'] == 'ok':
            return json_data['tick']
        raise Exception(f"请求{url}的数据发生错误, 错误信息--> {json_data}")

        # return self._request(RequestMethod.GET, path, params=params)

    def get_batch_funding_fee(self, symbol=None):
        path = '/swap-api/v1/swap_batch_funding_rate'
        url = self.host + path
        if symbol:
            params = {"contract_code": symbol}
            json_data = requests.get(url, params=params, timeout=self.timeout).json()
        else:
            json_data = requests.get(url,  timeout=self.timeout).json()

        if json_data['status'] == 'ok':
            return json_data['data']
        raise Exception(f"请求{url}的数据发生错误, 错误信息--> {json_data}")




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

    def contract_account_info(self, contract_code=None):
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
        path = "/swap-api/v1/swap_account_info"
        if contract_code:
            body = {'contract_code': contract_code
                }
        else:
            body = {}



        sign_data = self._sign('POST', path)

        url = self.host + path + '?' + self._build_params(sign_data)
        #print(url)
        #print(json.dumps(sign_data))  # ''
        # exit()

        headers = {"Content-Type": "application/json"}
        json_data = requests.post(url, headers=headers, data=json.dumps(body), timeout=self.timeout).json()
        if json_data['status'] == 'ok':
            return json_data['data']
        raise Exception(f"请求{url}发生错误...{json_data}")

    def get_transfer_limitation(self, contract_code):

        path = "/swap-api/v1/swap_transfer_limit"
        if contract_code:
            body = {'contract_code': contract_code
                }
        else:
            body = {}
        sign_data = self._sign('POST', path)

        url = self.host + path + '?' + self._build_params(sign_data)


        headers = {"Content-Type": "application/json"}
        json_data = requests.post(url, headers=headers, data=json.dumps(body), timeout=self.timeout).json()
        if json_data['status'] == 'ok':
            return json_data['data']
        raise Exception(f"请求{url}发生错误...{json_data}")

    def get_swap_account(self, contract_code):
        path = "/swap-api/v1/swap_account_info"
        if contract_code:
            body = {'contract_code': contract_code
                }
        else:
            body = {}
        sign_data = self._sign('POST', path)

        url = self.host + path + '?' + self._build_params(sign_data)


        headers = {"Content-Type": "application/json"}
        json_data = requests.post(url, headers=headers, data=json.dumps(body), timeout=self.timeout).json()
        if json_data['status'] == 'ok':
            return json_data['data']
        raise Exception(f"请求{url}发生错误...{json_data}")

    def change_leverage(self, symbol, leverage_rate):
        path = "/swap-api/v1/swap_switch_lever_rate"

        body = {'contract_code': symbol,
                'lever_rate': leverage_rate,
                }

        sign_data = self._sign('POST', path)

        url = self.host + path + '?' + self._build_params(sign_data)
        #print(url)
        #print(json.dumps(sign_data))  # ''
        # exit()

        headers = {"Content-Type": "application/json"}
        json_data = requests.post(url, headers=headers, data=json.dumps(body), timeout=self.timeout).json()
        #print(json_data)
        if json_data['status'] == 'ok':
            #print("successful in making contract order")
            print(f"leverate rate of {symbol} has been changed, current rate is {leverage_rate}")

        else:
            #print(json_data['data'])
            raise Exception(f"请求{url}发生错误...{json_data}")




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
        json_data = requests.get(url, headers={'Content-Type': 'application/json'}, timeout=self.timeout).json()
        # json_data = requests.get(url, timeout=self.timeout).json()
        if json_data['status'] == 'ok':
            return json_data['data']

        raise Exception(f"请求{url}的数据发生错误, 错误信息--> {json_data}")

        # return self._request(RequestMethod.GET, path, verify=True)

    #def get_account_accounts(self):
    #    path = '/v1/account/accounts'

    def place_order(self, contract_code, type, amount, direction, offset, lever_rate,  price=None,  tp_trigger_price=None, tp_order_price=None):
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
        path = "/swap-api/v1/swap_order"

        body = {'contract_code': contract_code,
                'volume': amount,
                'direction': direction,
                'offset': offset,
                'lever_rate': lever_rate,
                'order_price_type': type,
                }

        if price:
            body['price'] = str(price)

        if tp_trigger_price:
            body['tp_trigger-price'] = str(tp_trigger_price)

        if tp_order_price:
            body['tp_order_price'] = str(tp_order_price)

        sign_data = self._sign('POST', path)

        url = self.host + path + '?' + self._build_params(sign_data)
        #print(url)
        #print(json.dumps(sign_data))  # ''
        # exit()

        headers = {"Content-Type": "application/json"}
        try:
            json_data = requests.post(url, headers=headers, data=json.dumps(body), timeout=self.timeout).json()
        #print(json_data)
            if json_data['status'] == 'ok':
            #print("successful in making contract order")
                print(f"Create future order: {contract_code}, amount:{amount}, type: {type}")
                return 1
            else:
                #print(json_data['data'])
                return 0
                raise Exception(f"请求{url}发生错误...{json_data}")
        except:
            return 0



    def place_batchorder(self, contract_codes, type, volume, direction, offset, lever_rate,  price=None,  tp_trigger_price=None, tp_order_price=None):
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
        path = "/swap-api/v1/swap_batchorder"

        body = {'orders_data':[]}

        for contract_code in contract_codes:
            order = {}
            order['contract_code'] = contract_code
            order['volume'] = volume
            order['direction'] = direction
            order['offset'] = offset
            order['lever_rate'] = lever_rate
            order['order_price_type'] = type
            body['orders_data'].append(order)
        #print(body)
        #print("")

        if price:
            body['price'] = str(price)

        if tp_trigger_price:
            body['tp_trigger-price'] = str(tp_trigger_price)

        if tp_order_price:
            body['tp_order_price'] = str(tp_order_price)

        sign_data = self._sign('POST', path)

        url = self.host + path + '?' + self._build_params(sign_data)
        #print(url)
        #print(json.dumps(sign_data))  # ''
        # exit()

        headers = {"Content-Type": "application/json"}
        try:
            json_data = requests.post(url, headers=headers, data=json.dumps(body), timeout=self.timeout).json()
        #print(json_data)
            print(json_data)
            if json_data['status'] == 'ok':
            #print("successful in making contract order")
                if len(json_data['data']['errors']) == 0:
                    print(f"Create future batchorder: {contract_codes}, amount:{volume}, type: {type}")
                    return 1
                else:
                    raise Exception(f"请求{url}发生错误...{json_data}")
                    return 0
            else:
                #print(json_data['data'])
                return 0
                raise Exception(f"请求{url}发生错误...{json_data}")
        except:
            print("no response in placing batch order")
            return 0





    def get_account_balance(self, contract_code=None):

        path = "/swap-api/v1/swap_position_info"
        body = {}
        if contract_code:
            body['contract_code']: contract_code

        sign_data = self._sign('POST', path)

        url = self.host + path + '?' + self._build_params(sign_data)
        #print(url)
        #print(json.dumps(sign_data))  # ''
        # exit()

        headers = {"Content-Type": "application/json"}
        json_data = requests.post(url, headers=headers, data=json.dumps(body), timeout=self.timeout).json()
        #print(json_data)
        if json_data['status'] == 'ok':
            return(json_data['data'])
        #else:
            #return json_data['data']

        else:
            #print(json_data['data'])
            raise Exception(f"请求{url}发生错误...{json_data}")





    def get_index_price(self, contract_code):
        """
        查询指定账户的余额，支持以下账户：
        spot：现货账户， margin：杠杆账户，otc：OTC 账户，point：点卡账户
        :param account_id:
        :return:
        """
        path = '/swap-api/v1/swap_index'

        params = {'contract_code': contract_code,
        }
        #print(path)
        # exit()
        url = self.host + path
        sign_data = self._sign('GET', path, params=params)
        # print(sign_data)
        url += '?' + self._build_params(sign_data)
        #print(url)
        # exit()
        json_data = requests.get(url, timeout=self.timeout).json()
        #print(json_data)
        if json_data['status'] == 'ok':
            print("got index_price")
            return json_data['data']
        else:
            print("got index_price_failure")
            print(json_data)
            raise Exception(f"请求{url}的数据发生错误, 错误信息--> {json_data}")

    def get_kline(self, contract_code, period, size=100):
        """
        查询指定账户的余额，支持以下账户：
        spot：现货账户， margin：杠杆账户，otc：OTC 账户，point：点卡账户
        :param account_id:
        :return:
        """
        path = '/swap-ex/market/history/kline'

        params = {'contract_code': contract_code,
                  'period': period,
                  'size': size
                  }
        # print(path)
        # exit()
        try:
            response =  self._request(RequestMethod.GET, path, params=params)
            if response != 0:
                if len(response) != 0:
                    return response['data']
                else:
                    return 0
        except:
            print("timeout in getting kline data")
            return 0




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

        # return self._request(RequestMethod.GET, path, verify=True)

    def get_loan_info(self, symbol=None):
        path = '/v1/margin/loan-info'
        #url = self.host +path
        if symbol:
            params = {'symbols': symbol}
            sign_data = self._sign('GET', path, params=params)
        else:
            sign_data = self._sign('GET', path)
        url = self.host + path + '?' + self._build_params(sign_data)

        json_data = requests.get(url, timeout=self.timeout).json()

        if json_data['status'] == 'ok':
            return json_data['data']

        raise Exception(f'请求{url}发生错误..{json_data}')

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
        json_data = requests.post(url, headers=headers, data=json.dumps(body), timeout=self.timeout).json()
        #print(json_data)
        if json_data['status'] == 'ok':
            return json_data['data']
        else:
            return json_data

    def get_loanable_amt(self, symbol):
        info = self.get_loan_info(symbol)
        return info[0]['currencies'][0]['min-loan-amt'], info[0]['currencies'][0]['loanable-amt'], info[0]['currencies'][0]['max-loan-amt']

    def borrow_coin_order(self, symbol, currency, amt):
        path = '/v1/margin/orders'
        body = {'symbol': symbol, 'currency': currency, 'amount':amt}
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

    def get_loan_orders(self, symbol):
        path = '/v1/margin/loan-orders'

        # url = self.host +path
        #if symbol:
        #    params = {'symbols': symbol}
        #    sign_data = self._sign('GET', path, params=params)
        #else:
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
        print(json_data)
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

        if json_data['status'] == 'ok':
            return json_data['data']




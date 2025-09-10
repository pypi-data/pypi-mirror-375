# coding=utf-8
import hashlib


# 加签
class CSJMediaUtil:
    user_id = 0
    role_id = 0
    secure_key = "xxxxsecure_key"
    version = "2.0"
    sign_type_md5 = "MD5"
    KEY_USER_ID = "user_id"
    KEY_ROLE_ID = "role_id"
    KEY_VERDION = "version"
    KEY_SIGN = "sign"
    KEY_SIGN_TYPE = "sign_type"
    CSJ_HOST = "https://www.csjplatform.com"

    @classmethod
    def sign_gen(self, params):
        """Fetches sign .
        Args:
            params: a dict need to sign
            secure_key: string
        Returns:
            A dict. For example:
            {'url': 'a=1&sign_type=MD5&t=2&z=a&sign=4d0e069c1776f665583bc0f39d9d59795aa3cdff',
            'sign': '4d0e069c1776f665583bc0f39d9d59795aa3cdff'}
        """
        result = {
            "sign": "",
            "url": "",
        }
        try:
            if not isinstance(params, dict):
                return result
            if self.user_id != "":
                params[self.KEY_USER_ID] = self.user_id
            if self.role_id != "":
                params[self.KEY_ROLE_ID] = self.role_id
            params[self.KEY_VERDION] = self.version
            params[self.KEY_SIGN_TYPE] = self.sign_type_md5
            param_orders = sorted(params.items(), key=lambda x: x[0], reverse=False)
            raw_str = ""
            for k, v in param_orders:
                raw_str += (str(k) + "=" + str(v) + "&")
            print("raw sign_str: ", raw_str)
            if len(raw_str) == 0:
                return ""
            sign_str = raw_str[0:-1] + self.secure_key
            print("raw sign_str: ", sign_str)
            sign = hashlib.md5(sign_str.encode()).hexdigest()
            result[self.KEY_SIGN] = sign
            result["url"] = raw_str + "sign=" + sign
            return result
        except Exception as err:
            print("invalid Exception", err)
        return result

    @classmethod
    def get_signed_url(self, params):
        return self.sign_gen(params).get("url", "")

    @classmethod
    def get_media_rt_income(self, params):
        result = self.get_signed_url(params)
        if result == "":
            return ""
        return self.CSJ_HOST + "/union_media/open_api/rt/income?" + result


def get_aurora_sign(security_key, timestamp, nonce):
    keys = [security_key, str(timestamp), str(nonce)]
    keys.sort()
    keyStr = ''.join(keys)
    signature = hashlib.sha1(keyStr).hexdigest()

    return signature

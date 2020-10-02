import json
import time
from util.db_util import MysqlDb
import datetime

from util.request_util import RequestUtil
from util.send_email import SendMail


class InterfaceTestCase:

    def loadAllCaseByApp(self, app):
        my_db = MysqlDb()
        sql = "select * from `case` where app='{0}'".format(app)
        results = my_db.query(sql)
        return results

    def findCaseById(self, case_id):
        my_db = MysqlDb()
        sql = "select * from `case` where id='{0}'".format(case_id)
        results = my_db.query(sql, state="one")
        return results

    def loadConfigByAppAndKey(self, app, key):
        my_db = MysqlDb()
        sql = "select * from `config` where app='{0}' and dict_key='{1}'".format(app, key)
        results = my_db.query(sql, state="one")
        return results

    def updateResultByCaseId(self, response, is_pass, msg, case_id):
        my_db = MysqlDb()
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(current_time)
        if is_pass:
            sql = "update `case` set response='{0}', pass='{1}', msg='{2}', update_time='{3}' where id={4}".format("",
                                                                                                                   is_pass,
                                                                                                                   msg,
                                                                                                                   current_time,
                                                                                                                   case_id)
        else:
            sql = "update `case` set response=\"{0}\", pass='{1}', msg='{2}', update_time='{3}' where id={4}".format(
                str(response), is_pass, msg, current_time, case_id)
        rows = my_db.execute(sql)
        return rows

    def runAllCase(self, app):
        api_host_obj = self.loadConfigByAppAndKey(app, "host")
        results = self.loadAllCaseByApp(app)
        for case in results:
            if case['run'] == 'yes':
                try:
                    response = self.runCase(case, api_host_obj)
                    assert_msg = self.assertResponse(case, response)
                    rows = self.updateResultByCaseId(response, assert_msg['is_pass'], assert_msg['msg'], case['id'])
                    print("更新结果 rows={0}".format(str(rows)))

                except Exception as e:
                    print("用例id={0},标题:{1},执行报错:{2}".format(case['id'], case['title'], e))
        self.sendTestReport(app)

    def runCase(self, case, api_host_obj):
        headers = json.loads(case['headers'])
        body = json.loads(case['request_body'])
        method = case['method']
        req_url = api_host_obj['dict_value'] + case['url']

        if case["pre_case_id"] > -1:
            pre_case_id = case["pre_case_id"]
            pre_case = self.findCaseById(pre_case_id)
            pre_response = self.runCase(pre_case, api_host_obj)
            pre_assert_msg = self.assertResponse(pre_case, pre_response)
            if not pre_assert_msg['is_pass']:
                pre_response['msg'] = "前置条件不通过," + pre_response['msg']
                return pre_response
            pre_fields = json.loads(case['pre_fields'])
            for pre_field in pre_fields:
                if pre_field['scope'] == 'header':
                    for header in headers:
                        field_name = pre_field['field']
                        if header == field_name:
                            field_value = pre_response['data'][field_name]
                            headers[field_name] = field_value

                elif pre_field['scope'] == 'body':
                    print("替换body")
        req = RequestUtil()
        response = req.request(req_url, method, headers=headers, params=body)
        return response


    def assertResponse(self, case, response):
        assert_type = case['assert_type']
        expect_result = case['expect_result']
        is_pass = False
        if assert_type == 'code':
            response_code = response['code']
            if int(expect_result) == response_code:
                is_pass = True
            else:
                is_pass = False
        # 判断数组长度大小
        elif assert_type == 'data_json_array':
            data_array = response['data']
            if data_array is not None and isinstance(data_array, list) and len(data_array) > int(expect_result):
                is_pass = True
            else:
                is_pass = False
        elif assert_type == 'data_json':
            data = response['data']
            if data is not None and isinstance(data, dict) and len(data) > int(expect_result):
                is_pass = True
            else:
                is_pass = False

        msg = "模块:{0}, 标题:{1},断言类型:{2},响应:{3}".format(case['module'], case['title'], assert_type, response['msg'])

        # 拼装信息
        assert_msg = {"is_pass": is_pass, "msg": msg}
        return assert_msg

    def sendTestReport(self, app):
        results = self.loadAllCaseByApp(app)
        title = "接口自动化测试报告"
        content = """
               <html><body>
                   <h4>{0} 接口测试报告：</h4>
                   <table border="1">
                   <tr>
                     <th>编号</th>
                     <th>模块</th>
                     <th>标题</th>
                     <th>是否通过</th>
                     <th>备注</th>
                     <th>响应</th>
                   </tr>
                   {1}
                   </table></body></html>  
               """
        template = ""
        for case in results:
            template += "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td></tr>".format(
                case['id'], case['module'], case['title'], case['pass'], case['msg'], case['response']
            )

        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        content = content.format(current_time, template)
        mail_host = self.loadConfigByAppAndKey(app, "mail_host")['dict_value']
        mail_sender = self.loadConfigByAppAndKey(app, "mail_sender")['dict_value']
        mail_auth_code = self.loadConfigByAppAndKey(app, "mail_auth_code")['dict_value']
        mail_receivers = self.loadConfigByAppAndKey(app, "mail_receivers")['dict_value'].split(",")
        mail = SendMail(mail_host)
        mail.send(title, content, mail_sender, mail_auth_code, mail_receivers)


if __name__ == '__main__':
    test = InterfaceTestCase()
    test.runAllCase("小滴课堂")
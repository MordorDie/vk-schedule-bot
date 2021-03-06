import hashlib
import logging
import psycopg2
from datetime import datetime

organization_field_length = 15
faculty_field_length = 10
group_field_length = 5


class ScheduleDB:
    def __init__(self, config):
        self.con = psycopg2.connect(dbname=config["DB_NAME"], user=config["DB_USER"], password=config["DB_PASSWORD"], host=config["DB_HOST"])
        self.cur = self.con.cursor()

        logging.basicConfig(format='%(asctime)-15s [ %(levelname)s ] %(message)s',
                            filemode='a',
                            filename=config["LOG_DIR_PATH"] + "log-{0}.log".format(datetime.now().strftime("%Y-%m")))
        self.logger = logging.getLogger('db-logger')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.con.commit()
        self.con.close()

    @staticmethod
    def create_tag(organization, faculty, group):
        org_hash = hashlib.sha256(organization.encode('utf-8')).hexdigest()
        faculty_hash = hashlib.sha256(faculty.encode('utf-8')).hexdigest()
        group_hash = hashlib.sha256(group.encode('utf-8')).hexdigest()
        return org_hash[:organization_field_length] + \
               faculty_hash[:faculty_field_length] + \
               group_hash[:group_field_length]

    def add_lesson(self, tag, day, number, week_type, time_start, time_end, title, classroom, lecturer):
        try:
            self.cur.execute('INSERT INTO schedule(tag, day, "number", type, "startTime", "endTime", \
                             title, classroom, lecturer) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s);',
                             (tag, day, number, week_type, time_start, time_end, title, classroom, lecturer))
            self.con.commit()
            return True
        except BaseException as e:
            self.logger.warning('Add to schedule failed. Error: {0}. Data:\
                            tag={1},\
                            day={2},\
                            number={3},\
                            week_type={4},\
                            time_start={5},\
                            time_end={6},\
                            title={7},\
                            classroom={8},\
                            lecturer={9}'.format(
                str(e), tag, day, number, week_type, time_start, time_end, title, classroom, lecturer))
            return False

    def add_organization(self, organization, faculty, group):
        tag = self.create_tag(organization, faculty, group)
        try:
            self.cur.execute("INSERT INTO organizations(organization, faculty, studgroup, tag) VALUES(%s,%s,%s,%s);",
                             (organization, faculty, group, tag))
            self.con.commit()
            return tag
        except BaseException as e:
            self.logger.warning("Add organization failed. Error: {0}. Data:\
                            organization={1},\
                            faculty={2},\
                            group={3},\
                            tag={4}".format(str(e), organization, faculty, group, tag))
            return None

    def add_report(self, cid, report):
        try:
            self.cur.execute('INSERT INTO reports (type, user_id, report, date) VALUES(%s, %s, %s, %s)',
                             ('vk', cid, report, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            self.con.commit()
            return True
        except BaseException as e:
            self.logger.warning('Add report failed. Error: {0}. Data: cid={1}, report={2}'.format(str(e), cid, report))
            return False

    def add_user(self, cid, name, username, tag):
        try:
            self.cur.execute('INSERT INTO users VALUES(%s,%s,%s,%s,%s,null,null)', ('vk', cid, name, username, tag))
            self.con.commit()
            return True
        except BaseException as e:
            self.logger.warning('Add user failed. Error: {0}. Data: cid={1}, name={2}, username={3}, tag={4}'.format(
                str(e), cid, name, username, tag))
            raise e

    def update_user(self, cid, name, username, tag):
        try:
            self.cur.execute('UPDATE users SET "scheduleTag" = (%s) WHERE id = (%s)', (tag, cid))
            self.con.commit()
            return True
        except BaseException as e:
            self.logger.warning('Update user failed. Error: {0}. Data: cid={1}, name={2}, username={3}, tag={4}'.format(
                str(e), cid, name, username, tag))
            raise e

    def find_user(self, cid):
        try:
            self.cur.execute('SELECT "scheduleTag" FROM users WHERE id = (%s)', [cid])
            return self.cur.fetchone()
        except BaseException as e:
            self.logger.warning('Select user failed. Error: {0}. Data: cid={1}'.format(str(e), cid))
            raise e

    def find_users_where(self, auto_posting_time=None, is_today=None):
        try:
            if auto_posting_time is not None and is_today is not None:
                self.cur.execute('SELECT id, "scheduleTag" FROM users WHERE auto_posting_time = %s AND is_today = %s',
                                 (auto_posting_time, is_today))
                return self.cur.fetchall()
            elif auto_posting_time is not None:
                self.cur.execute('SELECT id, "scheduleTag" FROM users WHERE auto_posting_time = %s',
                                 (auto_posting_time))
                return self.cur.fetchall()
            elif is_today is not None:
                self.cur.execute('SELECT id, "scheduleTag" FROM users WHERE is_today = %s',
                                 (is_today))
                return self.cur.fetchall()
            else:
                self.cur.execute('SELECT id, "scheduleTag" FROM users')
                return self.cur.fetchall()
        except BaseException as e:
            self.logger.warning('Select users failed. Error: {0}. auto_posting_time={1}'.format(
                str(e), auto_posting_time))
            raise e

    def get_schedule(self, tag, day, week_type=-1):
        data = []
        try:
            if week_type != -1:
                self.cur.execute('SELECT number,title,classroom,type FROM schedule \
                            WHERE tag = (%s) AND day = (%s) AND (type = 2 OR type = %s) \
                            ORDER BY number, type ASC', (tag, day, week_type))
            else:
                self.cur.execute('SELECT number,title,classroom,type FROM schedule \
                            WHERE tag = (%s) AND day = (%s) ORDER BY number, type ASC', (tag, day))
            data = self.cur.fetchall()
        except BaseException as e:
            self.logger.warning('Select schedule failed. Error: {0}. Data: tag={1}, day={2}, week_type={3}'.format(
                str(e), tag, day, week_type))
            raise Exception
        finally:
            return data

    def get_organizations(self, tag=""):
        organizations = []
        try:
            self.cur.execute("SELECT organization, tag FROM organizations WHERE tag LIKE %s \
            GROUP BY organization", (tag + '%'))
            organizations = self.cur.fetchall()
        except BaseException as e:
            self.logger.warning('Select schedule failed. Error: {0}. Data: tag={1}'.format(str(e), tag))
            raise e
        finally:
            return organizations

    def get_faculty(self, tag=""):
        faculties = []
        try:
            self.cur.execute("SELECT faculty, tag FROM organizations WHERE tag LIKE %s GROUP BY faculty", (tag + '%'))
            faculties = self.cur.fetchall()
        except BaseException as e:
            self.logger.warning('Select schedule failed. Error: {0}. Data: tag={1}'.format(str(e), tag))
            raise e
        finally:
            return faculties

    def get_group(self, tag=""):
        group = []
        try:
            self.cur.execute("SELECT studGroup, tag FROM organizations WHERE tag LIKE %s GROUP BY studGroup",
                             (tag + '%'))
            group = self.cur.fetchall()
        except BaseException as e:
            self.logger.warning('Select group failed. Error: {0}. Data: tag={1}'.format(str(e), [tag]))
            raise e
        finally:
            return group

    def get_similar_organizations(self, org_name=""):
        org = []
        try:
            self.cur.execute('''
            SELECT tag,
            (organization || ' ' || faculty || ' ' || studgroup),
            similarity(lower(organization || ' ' || faculty || ' ' || studgroup), lower(%s))
            FROM organizations
            ORDER BY similarity(lower(organization || ' ' || faculty || ' ' || studgroup), lower(%s)) DESC LIMIT 5;''',
                             (org_name, org_name))
            org = self.cur.fetchall()
        except BaseException as e:
            self.logger.warning('Select similar organizations failed. Error: {0}. Data: tag={1}'.format(str(e), [org_name]))
            raise e
        finally:
            return org

    def set_auto_post_time(self, cid, time, is_today):
        try:
            self.cur.execute('UPDATE users SET auto_posting_time = %s, is_today = %s WHERE id = %s',
                             (time, is_today, cid))
            self.con.commit()
            return True
        except BaseException as e:
            self.logger.warning('Set auto post time failed. Error: {0}. Data: cid={1}, auto_posting_time={2}'.format(
                str(e), cid, time))
            raise e

    def clear_tables(self):
        try:
            self.cur.execute('DELETE FROM users;')
            self.cur.execute('DELETE FROM organizations;')
            self.cur.execute('DELETE FROM schedule;')
            self.cur.execute('DELETE FROM reports;')
            self.cur.execute('VACUUM')
            self.con.commit()
            return True
        except BaseException as e:
            self.logger.warning('clear tables failed. Error: {0}.'.format(
                str(e)))
            raise e

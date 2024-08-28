import json
import time
from typing import Union, List
from http import HTTPStatus

from titanclient.common.logger import logger
from titanclient.elliot.openapi.client import AuthenticatedClient, Client

from titanclient.elliot.openapi.api.batch import (
    post_project_pid_batch_config,
    post_project_pid_batch_gpl,
    post_project_pid_batch_latency,
    post_project_pid_batch_status,
    post_project_pid_batch_traffic_defaults,
    post_project_pid_batch_traffic_stats,
    put_project_pid_batch_traffic_pause,
    put_project_pid_batch_traffic_start,
    put_project_pid_batch_traffic_stats,
    put_project_pid_batch_traffic_stop)

from titanclient.elliot.openapi.api.docs import (
    get_docs_page,
    get_version)

from titanclient.elliot.openapi.api.login import (
    post_auth_login)

from titanclient.elliot.openapi.api.logs import (
    delete_project_pid_host_hid_log_lid_cache,
    get_project_pid_host_hid_log_lid_cache,
    get_project_pid_host_hid_log_lid_config_scenarios,
    get_project_pid_host_hid_log_lid,
    get_project_pid_host_hid_logs,
    post_project_pid_host_hid_log_lid_config,
    post_project_pid_host_hid_log_lid_gpl,
    post_project_pid_host_hid_log_lid_gpl_timeline,
    post_project_pid_host_hid_log_lid_latency,
    post_project_pid_host_hid_log_lid_status)

from titanclient.elliot.openapi.api.hosts import (
    delete_project_pid_host_hid,
    get_project_pid_host_hid_launch,
    get_project_pid_host_hid_shutdown,
    get_project_pid_host_hid,
    post_project_pid_host,
    put_project_pid_host_hid,)

from titanclient.elliot.openapi.api.projects import (
    delete_project_pid_usergroup_gid,
    delete_project_pid,
    get_project_pid_hosts_status,
    get_project_pid_hosts,
    get_project_pid_usergroups,
    get_project_pid,
    get_projects,
    post_project,
    put_project_pid_usergroup_gid,
    put_project_pid,)

from titanclient.elliot.openapi.api.permissions import (
    get_permissions)

from titanclient.elliot.openapi.api.traffic import (
    get_project_pid_host_hid_traffic_defaults,
    post_project_pid_host_hid_traffic_scenario_scenario,
    post_project_pid_host_hid_traffic_stats,
    put_project_pid_host_hid_traffic_pause,
    put_project_pid_host_hid_traffic_reset,
    put_project_pid_host_hid_traffic_scenario_scenario_pause,
    put_project_pid_host_hid_traffic_scenario_scenario_start,
    put_project_pid_host_hid_traffic_scenario_scenario_stop,
    put_project_pid_host_hid_traffic_start,
    put_project_pid_host_hid_traffic_stats,
    put_project_pid_host_hid_traffic_stop,)

from titanclient.elliot.openapi.api.usergroups import (
    delete_usergroup_gid_permission_peid,
    delete_usergroup_gid_user_uid,
    delete_usergroup_gid,
    get_usergroup_gid_members,
    get_usergroup_gid_permissions,
    get_usergroup_gid,
    get_usergroups,
    post_usergroup,
    put_usergroup_gid_permission_peid,
    put_usergroup_gid_user_uid,
    put_usergroup_gid)

from titanclient.elliot.openapi.api.reports import (
    get_project_pid_report_rid,
    get_project_pid_report_rid_xls,
    post_project_pid_report,
    post_project_pid_reports)

from titanclient.elliot.openapi.api.users import (
    delete_user_uid,
    get_me,
    get_user_uid,
    get_user_uid_projects,
    get_user_uid_usergroups,
    get_users,
    post_user,
    put_user_uid,
    put_user_uid_password)

from titanclient.elliot.openapi.api.values import (
    get_project_pid_value_name)

from titanclient.elliot.openapi.models import (
    credentials,
    log_spec,
    log_stat,
    log_stat_query,
    log as logmodel,
    gpl_timeline_query,
    gpl_timeline,
    host as hostmodel,
    new_user,
    permission,
    password_change,
    project,
    report,
    report_query,
    user,
    usergroup,
    new_usergroup,
    new_project,
    new_host,
    new_report,
    value_dict,
    value)


class ElliotClient:

    def __init__(self, url, username=None, password=None, mode="sync_detailed"):
        self.url = url
        self.mode = mode
        self._client = Client(base_url=self.url, verify_ssl=False)

        if username and password:
            self.login(username=username, password=password)

    def __repr__(self):
        return f"<ElliotClient {self.url}>"

    # helpers
    def call(self, module, **kwargs):
        resp = self._call_bare(module, **kwargs)

        # TODO: raise proper HTTP exceptions, look into httpx

        successes = [
            HTTPStatus.OK, 
            HTTPStatus.ACCEPTED, 
            HTTPStatus.NO_CONTENT]
        
        if resp.status_code not in successes:
            logger.error(resp.content)
            raise ValueError("Request unsuccessful", resp.status_code)
        
        if resp.parsed:
            return resp.parsed
        
        if resp.content:
            return json.loads(resp.content.decode())

    def _call_bare(self, module, **kwargs):
        return getattr(module, self.mode)(client=self._client, **kwargs)

    # openAPI bindings

    def login(self,  username=None, password=None):
        """
        Authenticate with username and password
        """
        c = credentials.Credentials(username=username, password=password)
        resp = self._call_bare(post_auth_login, body=c)
        token = resp.headers["authorization"].split(" ")[1]
        self._client = AuthenticatedClient(
            token=token,
            base_url=self.url,
            verify_ssl=False)

    def me(self) -> user.User:
        """
        Return current user

        Returns:
            user.User: User object of current user
        """
        return self.call(get_me)

    def users(self) -> list[user.User]:
        """
        Return list of users in system

        Returns:
            list[user.User]: list of User objects
        """
        return self.call(get_users)

    def user(self, uid: int) -> user.User:
        f"""
        Get user by `uid`.

        Args:
            uid (int): User id

        Returns:
            user.User: User object
        """
        return self.call(get_user_uid, uid=uid)

    def user_projects(self, uid: int) -> list[project.Project]:
        """
        Return list of projects user is member of.

        Args:
            uid (int): user id

        Returns:
            list[project.Project]: list of project objects
        """
        return self.call(get_user_uid_projects, uid=uid)

    def user_usergroups(self, uid: int) -> usergroup.Usergroup:
        """
        Return usergroups user with `uid` is member of

        Args:
            uid (int): User id

        Returns:
            list[usergroup.Usergroup]: list of Usergroups
        """
        return self.call(get_user_uid_usergroups, uid=uid)

    def create_user(self, name: str, roles: str) -> None:
        """
        Create user

        Args:
            name (str): User name
            roles (str): comma-separated role names
        """
        return self.call(post_user, body=new_user.NewUser(
            name=name,
            roles=roles))

    def update_user(self, uid: int, name: str, roles: str) -> None:
        """
        Update user

        Args:
            uid (int): User id
            name (str): User name
            roles (str): Comma-separated value names
        """
        return self.call(put_user_uid,
                         uid=uid,
                         body=new_user.NewUser(
                             name=name,
                             roles=roles))

    def update_user_password(self, uid: int, old: str, new: str) -> None:
        """
        Update user password

        Args:
            uid (int): User id
            old (str): Old password
            new (str): New password
        """
        return self.call(put_user_uid_password,
                         uid=uid, body=password_change.PasswordChange(old=old, new=new))

    def delete_user(self, uid: int) -> None:
        """
        Delete user

        Args:
            uid (int): User id
        """
        return self.call(delete_user_uid, uid=uid)

    def values(self,
               pid: int,
               name: str
               ) -> Union[list[value.Value], value_dict.ValueDict]:
        """
        Return available value names for multiple stat types

        Args:
            pid (int): Project id
            name (str): Name of stat type

        Returns:
            list[value.Value]: list of values of a given stat type
            value_dict.ValueDict: dictionary of all stat types
        """
        return self.call(get_project_pid_value_name, pid=pid, name=name)

    def create_report(
            self,
            pid: int,
            name: str,
            description: str,
            merged: bool,
            summarized: bool,
            timestamp: int,
            logs: list[log_spec.LogSpec],
            values: dict
            ):
        """
        Generate report

        Args:
            pid (int): project id
            name (str): report name
            description (str): description of report contents
            merged (bool): include merged worksheets
            summarized (bool): create summary worksheet
            timestamp (int): use GPL data from timestamp
            logs (list[log_spec.LogSpec]): log spec objects
            values (dict): dict of statistics objects values
        """
        logspecs = list(map(lambda l: log_spec.LogSpec(**l), logs))
        return self.call(post_project_pid_report,
                         pid=pid,
                         body=new_report.NewReport(
                             logs=logspecs,
                             values=values,
                             name=name,
                             description=description,
                             merged=merged,
                             summarized=summarized,
                             timestamp=timestamp))

    def reports(self, 
                pid: int,
                from_time: int = 0, 
                until_time: int = 0, 
                filter: str = ""
                ) -> list[report.Report]:
        
        return self.call(post_project_pid_reports, 
                         pid=pid,
                         body=report_query.ReportQuery(
                            from_time=from_time or time.time() - 604800, # one week
                            until_time=until_time or time.time(),
                            filter_=filter))

    def report(self, pid: int, rid: int) -> report.Report:
        """
        Return previously generated report object

        Args:
            pid (int): project id
            rid (int): report id

        Returns:
            report.Report: Report object
        """
        return self.call(get_project_pid_report_rid, pid=pid, rid=rid)

    def report_xls(self, pid: int, rid: int) -> bytes:
        """
        Download report XLS

        Args:
            pid (int): project id
            rid (int): report id

        Returns:
            octet stream (XLS file)
        """
        return self.call(get_project_pid_report_rid_xls, pid=pid, rid=rid)

    def delete_cache(self, pid: int, hid: int, lid: str) -> None:
        """
        Clear cache associated with log

        Args:
            pid (int): project id
            hid (int): host id
            lid (str): log UUID
        """
        return self.call(delete_project_pid_host_hid_log_lid_cache,
                         hid=hid, lid=lid)

    def cache(self,
              hid: int,
              lid: str
              ) -> list[value.Value]:

        return self.call(get_project_pid_host_hid_log_lid_cache,
                         hid=hid, lid=lid)

    def config_scenarios(self, pid: int, hid: int, lid: str) -> None:
        """
        Return scenarios associated with log config

        Args:
            pid (int): project id
            hid (int): host id
            lid (str): log id

        Returns:
            list[value.Value]: list of Scenario names
        """
        return self.call(
            get_project_pid_host_hid_log_lid_config_scenarios,
            pid=pid, hid=hid, lid=lid)

    def log(self, pid: int, hid: int, lid: str) -> logmodel.Log:
        """
        Return log information

        Args:
            pid (int): project id
            hid (int): host id
            lid (str): log id

        Returns:
            logmodel.Log: Log model object
        """
        return self.call(
            get_project_pid_host_hid_log_lid,
            pid=pid, hid=hid, lid=lid)

    def permissions(self) -> list[permission.Permission]:
        """
        Return list of available permissions.

        Returns:
            list[permission.Permission]: list of Permission objects
        """
        return self.call(get_permissions)

    def logs(self, pid: int, hid: int) -> List[logmodel.Log]:
        """
        Return list of logs on project host

        Args:
            pid (int): project id
            hid (int): host id

        Returns:
            List[logmodel.Log]: List of `Log` model objects
        """
        return self.call(get_project_pid_host_hid_logs,
                         pid=pid, hid=hid)

    def log_config(self, pid: int, hid: int, lid: str) -> log_stat.LogStat:
        """
        Return configuration stat values from log config

        Args:
            pid (int): project id
            hid (int): host id
            lid (str): log UUID

        Returns:
            log_stat.LogStat: Log statistics model object
        """
        return self.call(post_project_pid_host_hid_log_lid_config,
                         pid=pid, hid=hid, lid=lid)

    def log_gpl(self, pid: int, hid: int, lid: str):
        """
        Return GPL statistics for log

        Args:
            pid (int): project id
            hid (int): host id
            lid (str): log UUID

        Returns:
            log_stat.LogStat: Log statistics model object
        """
        return self.call(post_project_pid_host_hid_log_lid_gpl,
                         pid=pid, hid=hid, lid=lid)

    def log_gpl_timeline(
            self,
            pid: int,
            hid: int,
            lid: str,
            scenarios: list,
            stats: list
            ) -> gpl_timeline.GPLTimeline:
        """
        Return GPL Timeline for selected scenarios

        Args:
            pid (int): project id
            hid (int): host id
            lid (str): Log UUID
            scenarios (list): List of scenario names
            stats (list): List of GPL stat names

        Returns:
            gpl_timeline.GPLTimeline: GPL Timeline model object
        """
        return self.call(post_project_pid_host_hid_log_lid_gpl_timeline,
                         pid=pid, hid=hid, lid=lid,
                         body=gpl_timeline_query.GPLTimelineQuery(
                            scenarios=scenarios, stats=stats))

    def log_latency(
            self, 
            pid: int, 
            hid: int, 
            lid: str, 
            stats: list[str]
            ) -> list[log_stat.LogStat]:
        """
        Return Latency statistics of log

        Args:
            pid (int): project id
            hid (int): host id
            lid (str): log UUID
            stats (list[str]): list of request names

        Returns:
            list[log_stat.LogStat]: list of log statistics model object
        """
        return self.call(post_project_pid_host_hid_log_lid_latency,
                         pid=pid, hid=hid, lid=lid, body=stats)

    def log_status_codes(
            self, 
            pid: int, 
            hid: int, 
            lid: str
            ) -> list[log_stat.LogStat]:
        """
        Return status code statistics of log

        Args:
            pid (int): project id
            hid (int): host id
            lid (str): log UUID

        Returns:
            list[log_stat.LogStat]: list of log statistics model objects
        """
        return self.call(post_project_pid_host_hid_log_lid_status,
                         pid=pid, hid=hid, lid=lid, body=[])

    def log_config_batch(
            self,
            pid: int,
            logs: list[dict],
            stats: list[str]
            ) -> list[log_stat.LogStat]:
        """
        Return config values from multiple hosts. 

        Log spec format:
        {
            "hid": 1,
            "lid: <Log UUID>
        }

        Args:
            pid (int): project id
            logs (list[dict]): log specs
            stats (list[str]): list of config stat names

        Returns:
            list[log_stat.LogStat]: List of Log stat model objects
        """
        logspecs = list(map(lambda l: log_spec.LogSpec(**l), logs))
        return self.call(post_project_pid_batch_config,
                         pid=pid, 
                         body=log_stat_query.LogStatQuery(
                             logs=logspecs, stats=stats))

    def log_gpl_batch(
            self,
            pid: int,
            logs: list[dict],
            stats: list[str]
            ) -> list[log_stat.LogStat]:
        """
        Return GPL values from multiple hosts. 

        Log spec format:
        {
            "hid": 1,
            "lid: <Log UUID>
        }

        Args:
            pid (int): project id
            logs (list[dict]): log specs
            stats (list[str]): list of GPL stat names

        Returns:
            list[log_stat.LogStat]: List of Log stat model objects
        """

        logspecs = list(map(lambda l: log_spec.LogSpec(**l), logs))
        return self.call(post_project_pid_batch_gpl,
                         pid=pid, 
                         body=log_stat_query.LogStatQuery(
                             logs=logspecs, stats=stats))

    def log_latency_batch(
            self,
            pid: int,
            logs: list[dict],
            stats: list[str]
            ) -> list[log_stat.LogStat]:
        """
        Return latency values from multiple hosts. 

        Log spec format:
        {
            "hid": 1,
            "lid: <Log UUID>
        }

        Args:
            pid (int): project id
            logs (list[dict]): log specs
            stats (list[str]): list of latency stat names

        Returns:
            list[log_stat.LogStat]: List of Log stat model objects
        """

        logspecs = list(map(lambda l: log_spec.LogSpec(**l), logs))
        return self.call(post_project_pid_batch_latency,
                         pid=pid, 
                         body=log_stat_query.LogStatQuery(
                             logs=logspecs, stats=stats))

    def log_status_codes_batch(
            self,
            pid: int,
            logs: list[dict]
            ) -> list[log_stat.LogStat]:
        """
        Return status code values from multiple hosts. 

        Log spec format:
        {
            "hid": 1,
            "lid: <Log UUID>
        }

        Args:
            pid (int): project id
            logs (list[dict]): log specs

        Returns:
            list[log_stat.LogStat]: List of Log stat model objects
        """
    
        logspecs = list(map(lambda l: log_spec.LogSpec(**l), logs))
        return self.call(post_project_pid_batch_status,
                         pid=pid, 
                         body=log_stat_query.LogStatQuery(
                             logs=logspecs, stats=[]))

    def traffic_defaults(self, pid: int, hid: int):
        return self.call(get_project_pid_host_hid_traffic_defaults,
                         pid=pid, hid=hid)

    def traffic_stats(self, pid: int, hid: int):
        return self.call(post_project_pid_host_hid_traffic_stats,
                         pid=pid, hid=hid)

    def traffic_scenario(self, pid: int, hid: int, scenario: str):
        return self.call(post_project_pid_host_hid_traffic_scenario_scenario,
                         pid=pid, hid=hid, scenario=scenario)

    def start_traffic(self, pid: int, hid: int):
        """
        Start host traffic

        Args:
            pid (int): project id
            hid (int): host id
        """
        return self.call(put_project_pid_host_hid_traffic_start,
                        pid=pid, hid=hid)

    def stop_traffic(self, pid: int, hid: int):
        """
        Stop host traffic

        Args:
            pid (int): project id
            hid (int): host id
        """
        return self.call(put_project_pid_host_hid_traffic_stop,
                        pid=pid, hid=hid)

    def pause_traffic(self, pid: int, hid: int):
        """
        Pause traffic on host

        Args:
            pid (int): project id
            hid (int): host id

        Returns:
            None 
        """
        return self.call(put_project_pid_host_hid_traffic_pause,
                         pid=pid, hid=hid)

    def reset_traffic(self, pid: int, hid: int):
        """
        Reset traffic on host

        Args:
            pid (int): project id
            hid (int): host id

        Returns:
            None 
        """
        return self.call(put_project_pid_host_hid_traffic_reset,
                         pid=pid, hid=hid)

    def pause_scenario(self, pid: int, hid: int, scenario: str):
        """
        Pause host scenario traffic (set CPS to 0)

        Args:
            pid (int): project id
            hid (int): host id
            sceneario (str): scenario name

        Returns:
            None 
        """
        return self.call(put_project_pid_host_hid_traffic_scenario_scenario_pause,
                         pid=pid, hid=hid, scenario=scenario)

    def start_scenario(self, pid: int, hid: int, scenario: str):
        """
        Start host scenario traffic

        Args:
            pid (int): project id
            hid (int): host id
            sceneario (str): scenario name

        Returns:
            None 
        """
        return self.call(put_project_pid_host_hid_traffic_scenario_scenario_start,
                         pid=pid, hid=hid, scenario=scenario)

    def stop_scenario(self, pid: int, hid: int, scenario: str):
        """
        Stop host scenario traffic

        Args:
            pid (int): project id
            hid (int): host id
            sceneario (str): scenario name

        Returns:
            None 
        """
        return self.call(put_project_pid_host_hid_traffic_scenario_scenario_stop,
                         pid=pid, hid=hid, scenario=scenario)

    # TODO: figure out return values
    def traffic_defaults_batch(self):
        return self.call(post_project_pid_batch_traffic_defaults)

    def traffic_stats_batch(self, hids: list[int], stats: list[str]):
        return self.call(post_project_pid_batch_traffic_stats,
                         hids=hids, stats=stats)

    def traffic_pause_batch(self, pid: int, hids: list[int]):
        """
        Pause traffic on multiple hosts

        Args:
            pid (int): project id
            hids (list[int]): list of host ids

        Returns:
            None
        """
        return self.call(put_project_pid_batch_traffic_pause, hids=hids)

    def traffic_start_batch(self, pid: int, hids: list[int]):
        """
        Start traffic on multiple hosts

        Args:
            pid (int): project id
            hids (list[int]): list of host ids

        Returns:
            None
        """
        return self.call(put_project_pid_batch_traffic_start, hids=hids)

    def traffic_stop_batch(self, pid: int, hids: list[int]):
        return self.call(put_project_pid_batch_traffic_stop, hids=hids)

    def set_traffic_batch(self, pid: int):
        return self.call(put_project_pid_batch_traffic_stats)

    def docs_page(self, page: str):
        """
        Get Elliot documents page

        Args:
            page (str): page title

        Returns:
            dict: Document contents
        """
        return self.call(get_docs_page, page=page)

    def version(self):
        """
        Return Elliot version info

        Returns:
            Version info dict
        """
        return self.call(get_version)

    def delete_host(self, pid: int, hid: int):
        """
        Delete host from project

        Args:
            pid (int): project id
            hid (int): host id

        Returns:
            None
        """
        return self.call(delete_project_pid_host_hid,
                         pid=pid, hid=hid)

    def launch_host(self, pid: int, hid: int):
        """
        Launch TitanSim execution on host 

        Args:
            pid (int): project id
            hid (int): host id

        Returns:
            None
        """
        return self.call(get_project_pid_host_hid_launch,
                         pid=pid, hid=hid)

    def shutdown_host(self, pid: int, hid: int):
        """
        Shutdown TitanSim execution on host

        Args:
            pid (int): project id
            hid (int): host id

        Returns:
            None
        """
        return self.call(get_project_pid_host_hid_shutdown,
                         pid=pid, hid=hid)

    def host(self, pid: int, hid: int) -> hostmodel.Host:
        """
        Return host data

        Args:
            pid (int): project id
            hid (int): host id

        Returns:
            host.Host: Host model object
        """
        return self.call(get_project_pid_host_hid,
                         pid=pid, hid=hid)

    def create_host(
            self,
            pid: int,
            name: str,
            hostname: str,
            username: str,
            password: str,
            type: str,
            install_dir: str,
            config_file: str,
            pm_path: Union[str, None]):
        """
        Create host on project

        Args:
            pid (int): project id
            name (str): name of host
            hostname (str): URL/IP address 
            username (str): SSH username
            password (str): SSH password
            type (str): traffic/simulator type
            install_dir (str): TitanSim installation dir on host
            config_file (str): Configuration file to use for executions
            pm_path (Union[str, None]): PM storage path on host
        """
        return self.call(post_project_pid_host,
                         pid=pid,
                         body=new_host.NewHost(
                             type=type,
                             name=name,
                             hostname=hostname,
                             username=username,
                             password=password,
                             pm_path=pm_path,
                             install_dir=install_dir,
                             config_file=config_file))

    def update_host(self, **kwargs):
        """
        Update host values
        """
        return self.call(put_project_pid_host_hid, **kwargs)

    def delete_usergroup(self, pid: int, gid: int):
        """
        Delete usergroup

        Args:
            pid (int): project id
            gid (int): usergroup id

        Returns:
            None
        """
        return self.call(delete_project_pid_usergroup_gid, pid=pid, gid=gid)

    def delete_project(self, pid: int):
        """
        Delete project

        Args:
            pid (int): project id

        Returns:
            None
        """
        return self.call(delete_project_pid, pid=pid)

    def project_host_status(self, pid: int) -> list[dict]:
        """
        Return host statuses on project

        Args:
            pid (int): project id

        Returns:
            list[dict]: List of host status objects
        """
        return self.call(get_project_pid_hosts_status, pid=pid)

    def project_hosts(self, pid: int) -> list[hostmodel.Host]:
        """
        Return hosts on project

        Args:
            pid (int): project id

        Returns:
            list[host.Host]: List of project model objects
        """
        return self.call(get_project_pid_hosts, pid=pid)

    def project_usergroups(self, pid: int) -> list[usergroup.Usergroup]:
        """
        Return usergroups assigned to project

        Args:
            pid (int): project id

        Returns:
            list[usergroup.Usergroup]: List of usergroup model objects
        """
        return self.call(get_project_pid_usergroups, pid=pid)

    def project(self, pid: int):
        """
        Return project data

        Args:
            pid (int): project id

        Returns:
            project.Project: Project model object
        """
        return self.call(get_project_pid, pid=pid)

    def projects(self):
        """
        List projects

        Returns:
            list[project.Project]: list of Project model objects
        """
        return self.call(get_projects)

    def create_project(self, name: str):
        """
        Create project

        Args:
            name (str): project name

        Returns:
            None
        """
        return self.call(post_project, body=new_project.NewProject(name=name))

    def assign_usergroup(self, pid: int, gid: int):
        """
        Assign usergroup to project

        Args:
            pid (int): project id
            gid (int): usergroup id

        Returns:
            None
        """
        return self.call(put_project_pid_usergroup_gid, pid=pid, gid=gid)

    def update_project(self, name: str):
        """
        Update project values

        Args:
            name (str): project name

        Returns:
            None
        """
        return self.call(put_project_pid, name=name)

    def remove_permission(self, gid: int, peid: int):
        """
        Remove permission from usergroup

        Args:
            gid (int): usergroup id
            peid (int): permission id

        Returns:
            None
        """
        return self.call(delete_usergroup_gid_permission_peid, gid=gid, peid=peid)

    def remove_member(self, gid: int, uid: int):
        """
        Remove member from usergroup

        Args:
            gid (int): usergroup id
            uid (int): user id

        Returns:
            None
        """
        return self.call(delete_usergroup_gid_user_uid, gid=gid, uid=uid)

    def delete_usergroup(self, gid: int):
        """
        Delete usergroup

        Args:
            gid (int): usergroup id

        Returns:
            None
        """
        return self.call(delete_usergroup_gid, gid=gid)

    def usergroup_members(self, gid: int):
        """
        Return list of usergroup members

        Args:
            gid (int): usergroup id

        Returns:
            list[user.User]: List of user model objects
        """
        return self.call(get_usergroup_gid_members, gid=gid)

    def usergroup_permissions(self, gid: int):
        """
        Return usergroup permissions

        Args:
            gid (int): usergroup id

        Returns:
            list[permission.Permission]: List of permissions
        """
        return self.call(get_usergroup_gid_permissions, gid=gid)

    def usergroup(self, gid: int):
        """
        Return usergroup data

        Args:
            gid (int): usergroup id

        Returns:
            usergroup.Usergroup: Usergroup model object
        """
        return self.call(get_usergroup_gid, gid=gid)

    def usergroups(self):
        """
        Return list of usergroups

        Returns:
            list[usergroup.Usergroup]: List of Usergroup model objects
        """
        return self.call(get_usergroups)

    def create_usergroup(self, name: str):
        """
        Create new usergroup

        Args:
            name (str): usergroup name

        Returns:
            None
        """
        return self.call(post_usergroup, name=name)

    def add_permission(self, gid: int, peid: int):
        """
        Add permission to usergroup

        Args:
            gid (int): usergroup id
            peid (int): permission id

        Returns:
            None
        """
        return self.call(put_usergroup_gid_permission_peid, gid=gid, peid=peid)

    def add_member(self, gid: int, uid: int):
        """
        Add user to usergroup

        Args:
            gid (int): usergroup id
            uid (int): user id

        Returns:
            None 
        """
        return self.call(put_usergroup_gid_user_uid, gid=gid, uid=uid)

    def update_usergroup(self, gid: int, name: str):
        """
        Update usergroup

        Args:
            gid (int): usergroup id
            name (str): usergroup name

        Returns:
            None
        """
        return self.call(put_usergroup_gid,
                         gid=gid,
                         body=new_usergroup.NewUsergroup(name=name))

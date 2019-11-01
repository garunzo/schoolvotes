# School Votes / Community votes
#
# Author: Luca Cotter
#
# Date: August 2018
#
# (c) 2018 Copyright, Luca Cotter. All rights reserved.
#
from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from operator import itemgetter
from django.utils import timezone
from django.utils.timezone import localtime
import gc


import datetime

from votes.memoize import MWT

MWT_TIMEOUT = 60
MWT_TIMEOUT_SURVEY_OPEN = 10

SENIOREMAILS = "soa@smmk12.org;sla4@smmk12.org;ka3@smmk12.org;jna@smmk12.org;ada@smmk12.org;sha@smmk12.org;cga@smmk12.org;ba@smmk12.org;gsa@smmk12.org;jta@smmk12.org;awa2@smmk12.org;na2@smmk12.org;maa2@smmk12.org;sa3@smmk12.org;sa4@smmk12.org;aa8@smmk12.org;aa50@smmk12.org;ala3@smmk12.org;ama@smmk12.org;da5@smmk12.org;da4@smmk12.org;faa@smmk12.org;sna2@smmk12.org;jaa2@smmk12.org;bkb@smmk12.org;cmb2@smmk12.org;htb@smmk12.org;rbb3@smmk12.org;rb3@smmk12.org;dbb@smmk12.org;eab2@smmk12.org;tmb3@smmk12.org;bsb@smmk12.org;ljb@smmk12.org;akb@smmk12.org;whb2@smmk12.org;pdb@smmk12.org;aab8@smmk12.org;yob2@smmk12.org;aab5@smmk12.org;jkb@smmk12.org;alb6@smmk12.org;jab4@smmk12.org;jb3@smmk12.org;rjb@smmk12.org;emb4@smmk12.org;cab2@smmk12.org;cab12@smmk12.org;elb@smmk12.org;lcb@smmk12.org;njb2@smmk12.org;njb3@smmk12.org;nab2@smmk12.org;nab9@smmk12.org;ejb@smmk12.org;jnb2@smmk12.org;aob@smmk12.org;cpb@smmk12.org;jtb5@smmk12.org;amb15@smmk12.org;amb3@smmk12.org;slb6@smmk12.org;tmb2@smmk12.org;skb@smmk12.org;jjb@smmk12.org;egb3@smmk12.org;shb@smmk12.org;dsb3@smmk12.org;smb@smmk12.org;jjb2@smmk12.org;mrb@smmk12.org;fb@smmk12.org;cab11@smmk12.org;rdb@smmk12.org;kab@smmk12.org;jc5@smmk12.org;yvc@smmk12.org;ec@smmk12.org;ejc2@smmk12.org;mdc@smmk12.org;ic2@smmk12.org;wmc@smmk12.org;ojc@smmk12.org;jc3@smmk12.org;nac@smmk12.org;mac4@smmk12.org;kbc@smmk12.org;ac3@smmk12.org;snc@smmk12.org;clc@smmk12.org;sdc@smmk12.org;rc12@smmk12.org;ac21@smmk12.org;ac26@smmk12.org;eac3@smmk12.org;osc@smmk12.org;ac33@smmk12.org;cc@smmk12.org;sc@smmk12.org;brc@smmk12.org;dac@smmk12.org;jjc6@smmk12.org;gc2@smmk12.org;jrc6@smmk12.org;jrc8@smmk12.org;gc@smmk12.org;cac@smmk12.org;hac4@smmk12.org;lhc@smmk12.org;mjc@smmk12.org;arc10@smmk12.org;eac2@smmk12.org;jc4@smmk12.org;lac4@smmk12.org;ssc@smmk12.org;ec8@smmk12.org;aac2@smmk12.org;bc@smmk12.org;yc@smmk12.org;tcc@smmk12.org;bc7@smmk12.org;trc2@smmk12.org;nmc2@smmk12.org;hrd2@smmk12.org;jd7@smmk12.org;fnd@smmk12.org;rcd2@smmk12.org;jcd6@smmk12.org;pmd@smmk12.org;kld@smmk12.org;ajd@smmk12.org;mjd7@smmk12.org;dja3@smmk12.org;ckd@smmk12.org;ird@smmk12.org;jcd3@smmk12.org;ikd@smmk12.org;ssd2@smmk12.org;dd7@smmk12.org;yd@smmk12.org;vrd@smmk12.org;ald@smmk12.org;ald6@smmk12.org;ejd2@smmk12.org;pd@smmk12.org;sd@smmk12.org;ifd@smmk12.org;wad@smmk12.org;wad2@smmk12.org;amd2@smmk12.org;lcd5@smmk12.org;jed@smmk12.org;aad2@smmk12.org;dld@smmk12.org;jcd4@smmk12.org;mdd2@smmk12.org;nd@smmk12.org;aae@smmk12.org;lbe@smmk12.org;lbe2@smmk12.org;be@smmk12.org;mde@smmk12.org;rte@smmk12.org;rte2@smmk12.org;rte4@smmk12.org;nne@smmk12.org;eme@smmk12.org;eje@smmk12.org;dve@smmk12.org;cse@smmk12.org;sye@smmk12.org;yse@smmk12.org;je7@smmk12.org;rae@smmk12.org;rae2@smmk12.org;acf5@smmk12.org;ehf@smmk12.org;jaf@smmk12.org;lyf@smmk12.org;ndf@smmk12.org;maf@smmk12.org;maf3@smmk12.org;caf2@smmk12.org;hhf@smmk12.org;nd7@smmk12.org;gef2@smmk12.org;jbf@smmk12.org;clf@smmk12.org;ef@smmk12.org;plf@smmk12.org;mkf2@smmk12.org;mcg@smmk12.org;lbg3@smmk12.org;lbg4@smmk12.org;jdg2@smmk12.org;ajg@smmk12.org;eeg@smmk12.org;kg3@smmk12.org;kg10@smmk12.org;mg3@smmk12.org;mg4@smmk12.org;seg@smmk12.org;srg2@smmk12.org;ajg2@smmk12.org;ajg3@smmk12.org;nhg@smmk12.org;afg@smmk12.org;gig@smmk12.org;mag5@smmk12.org;nlg@smmk12.org;adg5@smmk12.org;agg2@smmk12.org;ikg@smmk12.org;irg@smmk12.org;xgg@smmk12.org;dmg2@smmk12.org;kag@smmk12.org;mkg2@smmk12.org;eg5@smmk12.org;fag@smmk12.org;fag2@smmk12.org;jig2@smmk12.org;mg6@smmk12.org;pg2@smmk12.org;sgg@smmk12.org;mag6@smmk12.org;bmg@smmk12.org;omg@smmk12.org;dag2@smmk12.org;wag@smmk12.org;mtg2@smmk12.org;acg@smmk12.org;acg2@smmk12.org;acg7@smmk12.org;kjg@smmk12.org;zrg@smmk12.org;afg2@smmk12.org;lzg@smmk12.org;wag2@smmk12.org;wag3@smmk12.org;aag3@smmk12.org;eg2@smmk12.org;eg4@smmk12.org;kng@smmk12.org;kng3@smmk12.org;ldg@smmk12.org;jag3@smmk12.org;meh@smmk12.org;nah@smmk12.org;iih@smmk12.org;iih4@smmk12.org;ssh8@smmk12.org;jh3@smmk12.org;woh@smmk12.org;gjh@smmk12.org;amh3@smmk12.org;nth@smmk12.org;jrh@smmk12.org;yh6@smmk12.org;ah2@smmk12.org;mhh@smmk12.org;cjh@smmk12.org;cjh2@smmk12.org;jkh2@smmk12.org;bvh@smmk12.org;bvh2@smmk12.org;dh@smmk12.org;mlh2@smmk12.org;sh@smmk12.org;jh4@smmk12.org;rph2@smmk12.org;hah2@smmk12.org;eeh3@smmk12.org;th@smmk12.org;nbh@smmk12.org;aah@smmk12.org;bmh3@smmk12.org;vmh@smmk12.org;hh@smmk12.org;mmh@smmk12.org;hkh@smmk12.org;jsh@smmk12.org;geh@smmk12.org;ash2@smmk12.org;elh2@smmk12.org;elh3@smmk12.org;ceh@smmk12.org;sti@smmk12.org;ai@smmk12.org;si2@smmk12.org;mmi2@smmk12.org;ajj@smmk12.org;mrj@smmk12.org;jaj@smmk12.org;cgj2@smmk12.org;dmj2@smmk12.org;ckj@smmk12.org;rjj@smmk12.org;fj2@smmk12.org;adj@smmk12.org;fj@smmk12.org;jej@smmk12.org;aaj2@smmk12.org;osj@smmk12.org;gvj@smmk12.org;baj@smmk12.org;gsj@smmk12.org;mkj3@smmk12.org;amj8@smmk12.org;nlj@smmk12.org;ek@smmk12.org;mmk@smmk12.org;grk@smmk12.org;grk4@smmk12.org;mrk@smmk12.org;ak5@smmk12.org;vk2@smmk12.org;cak@smmk12.org;ltk@smmk12.org;cik@smmk12.org;jak@smmk12.org;bmk2@smmk12.org;jmk2@smmk12.org;wrk2@smmk12.org;bbk@smmk12.org;ltk2@smmk12.org;gek@smmk12.org;jmk@smmk12.org;srk2@smmk12.org;kmk2@smmk12.org;csk5@smmk12.org;jk7@smmk12.org;vk@smmk12.org;lgk@smmk12.org;nrk@smmk12.org;ksl2@smmk12.org;zml@smmk12.org;ail2@smmk12.org;jl@smmk12.org;zsl2@smmk12.org;mtl@smmk12.org;pll2@smmk12.org;ayl5@smmk12.org;gml@smmk12.org;gdl@smmk12.org;ltl@smmk12.org;tml@smmk12.org;evl@smmk12.org;sl3@smmk12.org;bcl@smmk12.org;mrl@smmk12.org;kml@smmk12.org;kml2@smmk12.org;jrl@smmk12.org;abl2@smmk12.org;bal2@smmk12.org;vl@smmk12.org;jal@smmk12.org;yl@smmk12.org;ial@smmk12.org;ial7@smmk12.org;aml14@smmk12.org;bjl@smmk12.org;djl@smmk12.org;el@smmk12.org;fal@smmk12.org;lsl3@smmk12.org;nbl2@smmk12.org;vel@smmk12.org;gal@smmk12.org;gal2@smmk12.org;drl@smmk12.org;lsl@smmk12.org;aal@smmk12.org;aml2@smmk12.org;aml15@smmk12.org;ael@smmk12.org;dmm5@smmk12.org;lmm4@smmk12.org;cjm5@smmk12.org;cjm16@smmk12.org;rm2@smmk12.org;wbm@smmk12.org;aem2@smmk12.org;hcm@smmk12.org;hcm2@smmk12.org;hm@smmk12.org;rm@smmk12.org;am4@smmk12.org;bdm@smmk12.org;ckm@smmk12.org;nwm@smmk12.org;njm2@smmk12.org;cm3@smmk12.org;enm@smmk12.org;fam3@smmk12.org;jcm@smmk12.org;sam2@smmk12.org;um@smmk12.org;rim@smmk12.org;fjm@smmk12.org;km5@smmk12.org;km6@smmk12.org;mpm@smmk12.org;gkm4@smmk12.org;tlm2@smmk12.org;cnm2@smmk12.org;gcm@smmk12.org;cjm4@smmk12.org;cjm3@smmk12.org;pam4@smmk12.org;adm@smmk12.org;bem2@smmk12.org;aam2@smmk12.org;clm@smmk12.org;etm@smmk12.org;egm@smmk12.org;smm@smmk12.org;sam3@smmk12.org;nm@smmk12.org;jjm3@smmk12.org;sbm@smmk12.org;sbm2@smmk12.org;egm2@smmk12.org;rm3@smmk12.org;nlm5@smmk12.org;cm17@smmk12.org;ifm@smmk12.org;ipm@smmk12.org;jkm2@smmk12.org;dsm@smmk12.org;dsm2@smmk12.org;gam2@smmk12.org;gam3@smmk12.org;em26@smmk12.org;em@smmk12.org;gem2@smmk12.org;tm2@smmk12.org;am3@smmk12.org;edm2@smmk12.org;kam2@smmk12.org;ljm11@smmk12.org;gem@smmk12.org;glm2@smmk12.org;sam@smmk12.org;spm@smmk12.org;nmm@smmk12.org;cxm@smmk12.org;cdm4@smmk12.org;gjm@smmk12.org;mhm2@smmk12.org;tlm@smmk12.org;hlm@smmk12.org;imm3@smmk12.org;nfm@smmk12.org;am6@smmk12.org;am7@smmk12.org;tan2@smmk12.org;tmn2@smmk12.org;an9@smmk12.org;en@smmk12.org;osn@smmk12.org;aln6@smmk12.org;jjn@smmk12.org;cdn@smmk12.org;mbn@smmk12.org;mbn2@smmk12.org;wln@smmk12.org;wln2@smmk12.org;imn@smmk12.org;ajn@smmk12.org;kvn@smmk12.org;an7@smmk12.org;hcn@smmk12.org;do@smmk12.org;jco@smmk12.org;rao@smmk12.org;ro@smmk12.org;kgo@smmk12.org;zao@smmk12.org;zao2@smmk12.org;jo@smmk12.org;jto@smmk12.org;rlo@smmk12.org;jco2@smmk12.org;aro@smmk12.org;lro@smmk12.org;ago2@smmk12.org;ago3@smmk12.org;tco@smmk12.org;ljo@smmk12.org;ako@smmk12.org;ako3@smmk12.org;eo@smmk12.org;iso@smmk12.org;kmo@smmk12.org;kho@smmk12.org;gao@smmk12.org;ap4@smmk12.org;ap3@smmk12.org;dlp@smmk12.org;kp3@smmk12.org;rap@smmk12.org;bp2@smmk12.org;mrp2@smmk12.org;erp@smmk12.org;ckp@smmk12.org;dp2@smmk12.org;smp@smmk12.org;oyp@smmk12.org;gdp@smmk12.org;ewp@smmk12.org;glp@smmk12.org;srp@smmk12.org;jjp@smmk12.org;jrp@smmk12.org;ncp@smmk12.org;jrp7@smmk12.org;jbp3@smmk12.org;ecp@smmk12.org;obp@smmk12.org;ohp@smmk12.org;vp@smmk12.org;bdp@smmk12.org;amq@smmk12.org;sq@smmk12.org;mrr7@smmk12.org;lnr@smmk12.org;nar@smmk12.org;okr@smmk12.org;ajr2@smmk12.org;rir@smmk12.org;ar5@smmk12.org;ejr@smmk12.org;ejr2@smmk12.org;iir@smmk12.org;iir2@smmk12.org;jer@smmk12.org;car@smmk12.org;mlr5@smmk12.org;dlr@smmk12.org;izr@smmk12.org;jar2@smmk12.org;zmr2@smmk12.org;lnr3@smmk12.org;sr@smmk12.org;imr@smmk12.org;gar@smmk12.org;hfr@smmk12.org;sir@smmk12.org;lr7@smmk12.org;clr@smmk12.org;dfr@smmk12.org;mcr@smmk12.org;rgr@smmk12.org;mr3@smmk12.org;dar4@smmk12.org;gar2@smmk12.org;rrr@smmk12.org;rrr2@smmk12.org;apr2@smmk12.org;egr@smmk12.org;sbr3@smmk12.org;mlr4@smmk12.org;jr4@smmk12.org;zir@smmk12.org;dzr@smmk12.org;jfr@smmk12.org;jr3@smmk12.org;ajs2@smmk12.org;ns16@smmk12.org;ms3@smmk12.org;sms2@smmk12.org;ms4@smmk12.org;ms2@smmk12.org;zcs@smmk12.org;cds@smmk12.org;mks@smmk12.org;das4@smmk12.org;kds2@smmk12.org;ks2@smmk12.org;kis4@smmk12.org;is2@smmk12.org;ns2@smmk12.org;jbs@smmk12.org;aps4@smmk12.org;ss2@smmk12.org;mws5@smmk12.org;sws2@smmk12.org;rts@smmk12.org;sgs2@smmk12.org;aas2@smmk12.org;djs@smmk12.org;tps@smmk12.org;fls@smmk12.org;kvs@smmk12.org;njs@smmk12.org;cas@smmk12.org;dms@smmk12.org;ahs@smmk12.org;ihs@smmk12.org;sjs3@smmk12.org;as7@smmk12.org;acs2@smmk12.org;ms29@smmk12.org;as32@smmk12.org;bcs2@smmk12.org;wds@smmk12.org;cas16@smmk12.org;hss@smmk12.org;hss2@smmk12.org;ghs@smmk12.org;hrs3@smmk12.org;ors@smmk12.org;bcs@smmk12.org;mms12@smmk12.org;ris@smmk12.org;as4@smmk12.org;nys@smmk12.org;jbs12@smmk12.org;scs@smmk12.org;las8@smmk12.org;njs6@smmk12.org;sao@smmk12.org;sao2@smmk12.org;sgs3@smmk12.org;ijs@smmk12.org;tes4@smmk12.org;bas10@smmk12.org;sks2@smmk12.org;ins2@smmk12.org;lps@smmk12.org;tls3@smmk12.org;gms5@smmk12.org;bas2@smmk12.org;sss6@smmk12.org;tjs@smmk12.org;jas14@smmk12.org;st15@smmk12.org;tt@smmk12.org;jtt3@smmk12.org;edt@smmk12.org;smt@smmk12.org;kbt@smmk12.org;lrt@smmk12.org;lrt5@smmk12.org;kst2@smmk12.org;kdt@smmk12.org;jmt5@smmk12.org;sdt4@smmk12.org;crt@smmk12.org;njt@smmk12.org;mt4@smmk12.org;rvt@smmk12.org;adt@smmk12.org;gft@smmk12.org;kyt@smmk12.org;cit@smmk12.org;sv4@smmk12.org;npv@smmk12.org;aav@smmk12.org;jv@smmk12.org;tiv@smmk12.org;ajv@smmk12.org;ov@smmk12.org;gv@smmk12.org;pcv@smmk12.org;siv@smmk12.org;orv@smmk12.org;ojv@smmk12.org;ojv2@smmk12.org;lav@smmk12.org;mv@smmk12.org;mv10@smmk12.org;igv@smmk12.org;kav@smmk12.org;jjv@smmk12.org;nv@smmk12.org;wav2@smmk12.org;jmv3@smmk12.org;nmv@smmk12.org;dnw@smmk12.org;azw@smmk12.org;smw@smmk12.org;emw2@smmk12.org;ww2@smmk12.org;eaw@smmk12.org;ajw@smmk12.org;hjw3@smmk12.org;sfw@smmk12.org;nww@smmk12.org;amw@smmk12.org;kmw2@smmk12.org;ddw2@smmk12.org;ebw@smmk12.org;lnw@smmk12.org;yaw@smmk12.org;yaw2@smmk12.org;aew2@smmk12.org;aew3@smmk12.org;ccw@smmk12.org;srw@smmk12.org;rzx@smmk12.org;afy@smmk12.org;zy@smmk12.org;jyy@smmk12.org;sfy@smmk12.org;aay@smmk12.org;kky2@smmk12.org;jy@smmk12.org;aez@smmk12.org;jz@smmk12.org;djz@smmk12.org;ijz@smmk12.org;cz2@smmk12.org;alz@smmk12.org;jaz@smmk12.org;smz@smmk12.org;rob1995@gmail.com"

# Create your models here.
class Community(models.Model):
    cid = models.CharField(max_length=64, help_text='max chars = 64')
    name = models.CharField(max_length=64, help_text='max chars = 64')
    # https://coderwall.com/p/bz0sng/simple-django-image-upload-to-model-imagefield
    logo = models.ImageField(upload_to = 'logos', default = 'logos/no-img.jpg')
    emails = models.CharField(max_length=65536, blank=True, default='', help_text='max chars = 65536')

    class Meta:
        verbose_name_plural = "Communities"

    def __str__(self):
        return f"Community Code: {self.cid}, Name: {self.name}, logo: {self.logo}"

    @MWT(MWT_TIMEOUT)
    def get_surveys(self):
        return Survey.objects.filter(community=self).order_by('create_date_time')

    @MWT(MWT_TIMEOUT)
    def get_surveys_not_hidden(self):
        return Survey.objects.filter(community=self, hide=False).order_by('create_date_time')

    def get_emails(self):
        return self.emails

    @staticmethod
    @MWT(MWT_TIMEOUT)
    def get_community_by_id(community_id):
        try:
            community = Community.objects.get(pk=community_id)
        except ObjectDoesNotExist:
            return None
        return community

    def get_name(self):
        return self.name

    @staticmethod
    @MWT(MWT_TIMEOUT)
    def get_community(username):
        try:
            community = CommunityUser.objects.get(username=username)
        except ObjectDoesNotExist:
            return None
        return community

    @staticmethod
    @MWT(MWT_TIMEOUT)
    def get_communities():
        return Community.objects.all()

    @staticmethod
    @MWT(MWT_TIMEOUT)
    def get_communities_matching_email(useremail):
        communities = Community.get_communities()
        community_list = []
        for community in communities:
            if community.email_authorized(useremail):
                community_list.append(community)
        return community_list

    @MWT(MWT_TIMEOUT)
    def email_authorized(self, useremail):
        email_list = list(filter(None, self.get_emails().split(';')))
        if len(email_list) == 0:
            return True
        else:
            for email in email_list:
                if email in useremail:
                    return True

        # Enable seniors
        if self.cid == "333333":
            email_list = list(filter(None, SENIOREMAILS.split(';')))
            if len(email_list) != 0:
                for email in email_list:
                    if email in useremail:
                        return True
        return False

    @MWT(MWT_TIMEOUT)
    def get_logo():
        path_elements = self.logo.split('/')
        print(path_elements)
        items = len(path_elements)
        print(path_elements[items-1])
        return path_elements[items-1]

class CommunityUser(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    username = models.CharField(max_length=64)


class Survey(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    description = models.CharField(max_length=80)
    create_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    expiration_date_time = models.DateField(default=datetime.date.today)
    hide = models.BooleanField(default=False,
        help_text="Hide survey from community list")
    max_votes = models.IntegerField(default=0)
    results_hidden = models.BooleanField(default=False)
    survey_auto_open_close = models.BooleanField(default=False, \
        help_text="Set to true to close survey automatically based on " + \
                  "survey_open_datetime and survey_close_datetime. " + \
                  "Note that value is cached for " + str(MWT_TIMEOUT) + \
                  " seconds")
    survey_open_datetime = models.DateTimeField(default=timezone.now, null=True)
    survey_close_datetime = models.DateTimeField(default=timezone.now, null=True)

    @MWT(MWT_TIMEOUT_SURVEY_OPEN)
    def is_closed(self):
        return self.survey_auto_open_close and \
               (timezone.now() < self.survey_open_datetime or \
               timezone.now() > self.survey_close_datetime)

    @MWT(MWT_TIMEOUT_SURVEY_OPEN)
    def has_not_closed_yet(self):
        return self.survey_auto_open_close and (timezone.now() < self.survey_close_datetime)

    @MWT(MWT_TIMEOUT_SURVEY_OPEN)
    def get_open_datetime_str(self):
        return localtime(self.survey_open_datetime).strftime('%m-%d-%Y %I:%M %p')

    @MWT(MWT_TIMEOUT_SURVEY_OPEN)
    def get_close_datetime_str(self):
        return localtime(self.survey_close_datetime).strftime('%m-%d-%Y %I:%M %p')

    def __str__(self):
      return f"Survey: {self.description}, Community: {self.community.name}"

    def add_question(self, rank, text):
        question = Question(survey = self, _rank = rank, _text = text)
        question.save()
        return question

    def del_question(self, question):
        question.delete()

    @MWT(MWT_TIMEOUT)
    def get_questions(self):
        return Question.objects.filter(survey=self).order_by('_rank')

    @MWT(MWT_TIMEOUT)
    def get_description(self):
        return self.description

    def get_community(self):
        return self.community

    @MWT(MWT_TIMEOUT)
    def isHidden(self):
        return self.hide

    @MWT(MWT_TIMEOUT)
    def get_max_votes(self):
        return self.max_votes

    @MWT(MWT_TIMEOUT)
    def results_are_hidden(self):
        return self.results_hidden


    def get_user_votes(self, email):
        survey_voters = SurveyVoter.objects.filter(survey=self, email = email)
        if len(survey_voters) > 1:
            print("Inconsistency, more than one surveyvoter record.")
            return survey_voters[0].get_vote_count()
        elif len(survey_voters) == 1:
            return survey_voters[0].get_vote_count()
        else:
            return 0

    @MWT(MWT_TIMEOUT)
    def user_authorized(self, email):
        return self.community.email_authorized(email)

    @staticmethod
    @MWT(MWT_TIMEOUT)
    def user_athorized(email, sid):
        survey = Survey.get_survey_by_id(sid)
        return survey.user_authorized(email)

    @staticmethod
    @MWT(MWT_TIMEOUT)
    def get_survey_by_id(survey_id):
        try:
            survey = Survey.objects.get(pk=survey_id)
        except ObjectDoesNotExist:
            return None
        return survey

    @staticmethod
    @MWT(MWT_TIMEOUT)
    def get_response_percents(survey_id):
        try:
            survey = Survey.objects.get(pk=survey_id)
        except ObjectDoesNotExist:
            return None
        response_counts = []
        for question in Question.objects.filter(survey = survey).order_by('_rank'):
            num_votes = 0
            for response in question.get_responses():
                num_votes += response.votes()
            for response in question.get_responses():
                rid = str(response.id)
                vote_count = response.votes()
                if num_votes != 0:
                    percent = int(vote_count * 100.0 / num_votes)
                else:
                    percent = 0
                response_counts.append([rid, percent, vote_count])
        return response_counts

class SurveyVoter(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    username = models.CharField(max_length=64)
    email = models.CharField(max_length=254,
                             blank=False)
    vote_count = models.IntegerField(default=1)
    created     = models.DateTimeField(editable=False)
    modified    = models.DateTimeField()

    def __str__(self):
        return f"Survey: {self.survey}, email: {self.email}, vote count: {self.vote_count}"

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(SurveyVoter, self).save(*args, **kwargs)

    def get_vote_count(self):
        return self.vote_count

    @classmethod
    def update_vote_record(cls, survey, username, email):
        with transaction.atomic():
            survey_voter, created = cls.objects.get_or_create(email = email, survey = survey,
                            defaults={'username':username})
            if not created:
                # survey_voter = (cls.objects.select_for_update().get(id=record.id))
                if survey.get_max_votes() == 0:
                    survey_voter.vote_count += 1
                    survey_voter.save()
                    status = True
                elif survey.get_max_votes() > survey_voter.vote_count:
                    survey_voter.vote_count += 1
                    survey_voter.save()
                    status = True
                else:
                    status = False
            else:
                # No voting had occurred, so okay to vote
                status = True
        return (status, survey_voter.vote_count)

    @classmethod
    def decr_vote_record(cls, survey, username, email):
        with transaction.atomic():
            survey_voter = cls.objects.get(email = email, survey = survey)
            survey_voter.vote_count -= 1
            survey_voter.save()
            status = True
        return status

class Question(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    _rank = models.IntegerField(default=0)
    _text = models.CharField(max_length=256)
    response_limit = models.IntegerField(default=1)

    def __str__(self):
        # return f"Survey: {self.survey.description}, Rank: {self.rank}, Question Text: {self.text}, id: {self.id}"

        return f"Survey: , Rank: {self.rank()}, Question Text: {self.text()}, qid: {self.id}"

    @MWT(MWT_TIMEOUT)
    def get_responses(self):
        responses = Response.objects.filter(question=self).order_by('_rank')
        return responses

    def get_responses_by_votes(self):
        responses = Response.objects.filter(question=self).order_by('_rank')
        response_list = []
        for response in responses:
            votes = response.votes()
            response_list.append([response, votes])
        response_list = sorted(response_list, key=itemgetter(1), reverse=True)
        responses = []
        for response in response_list:
            responses.append(response[0])
        return responses

    def rank(self):
        return self._rank

    def text(self):
        return self._text

    def has_voted(self, username):
        vote = ResponseVote.objects.filter(question = self, username = username)
        return len(vote) > 0

    def add_response(self, rank, text):
        response = Response(question = self, _rank = rank, _text = text)
        response.save()
        return response

    def get_survey(self):
        return self.survey

    @MWT(MWT_TIMEOUT)
    def get_response_limit(self):
        return self.response_limit

    @staticmethod
    @MWT(MWT_TIMEOUT)
    def get_question_by_id(question_id):
        try:
            question = Question.objects.get(pk=question_id)
        except ObjectDoesNotExist:
            return None
        return question

class Response(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    _rank = models.IntegerField(default = 0)
    _text = models.CharField(max_length=80)
    image_path = models.CharField(max_length=160, null=False, blank=True, default="")

    def __str__(self):
        return f"Survey: {self.question.survey.description}, Rank: {self.rank()}, Question: {self.question.text()}, Response: {self.text()}"

    def votes(self):
        return ResponseVote.objects.filter(response=self).count()

    def vote(self, username, email):
        vote = ResponseVote(response = self, question = self.question, username = username, email = email)
        vote.save()
        return True

    def rank(self):
        return self._rank

    def text(self):
        return self._text

    def get_survey(self):
        return self.question.get_survey()

    def get_image_path(self):
        return self.image_path

    def has_image(self):
        is_empty  = self.image_path in (None, '') or not self.image_path.strip()
        return not is_empty

    @MWT(MWT_TIMEOUT)
    def user_authorized(self, email):
        return self.question.survey.community.email_authorized(email)

    @staticmethod
    @MWT(MWT_TIMEOUT)
    def get_response_by_id(response_id):
        try:
            response = Response.objects.get(pk=response_id)
        except ObjectDoesNotExist:
            return None
        return response

class ResponseVote(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    response = models.ForeignKey(Response, on_delete=models.CASCADE)
    username = models.CharField(max_length=64)
    email = models.CharField(max_length=254, null=True, blank=False)

    @staticmethod
    def batch_qs(qs, batch_size=1000):
        """
        Returns a (start, end, total, queryset) tuple for each batch in the given
        queryset.

        Usage:
            # Make sure to order your querset
            article_qs = Article.objects.order_by('id')
            for start, end, total, qs in batch_qs(article_qs):
                print "Now processing %s - %s of %s" % (start + 1, end, total)
                for article in qs:
                    print article.body
        """
        total = qs.count()
        for start in range(0, total, batch_size):
            end = min(start + batch_size, total)
            yield (start, end, total, qs[start:end])
            gc.collect()

    @staticmethod
    def queryset_iterator(queryset, chunksize=1000):
        pk = 0
        last_pk = queryset.order_by('-pk')[0].pk
        queryset = queryset.order_by('pk')
        while pk < last_pk:
            for row in queryset.filter(pk__gt=pk)[:chunksize]:
                pk = row.pk
                yield row
            gc.collect()

    @staticmethod
    def dump_votes1(f):
        response_vote_qs = ResponseVote.objects.order_by('id')
        for start, end, total, qs in ResponseVote.batch_qs(response_vote_qs):
            for rv in qs:
                f.write(str(rv.csv_record()))
        return

    @staticmethod
    def dump_votes2(f):
        for rv in ResponseVote.queryset_iterator(ResponseVote.objects.all()):
            f.write(str(rv.csv_record())+"\n")
            f.flush()
        return

    @staticmethod
    def dump_votes(f):
        for rv in ResponseVote.objects.order_by('id').all()[10000:15000]:
            f.write(str(rv.csv_record()))
            f.flush()
        return

    def csv_record(self):
        csv = str(self.id) + ", '" + self.response.question.survey.description + "', '" + self.response.question.text() + "', '" + self.response.text() + "', '" + self.username + "', '" + str(self.email) + "'\n"
        return csv

    def __str__(self):
        return f"Survey: {self.response.question.survey.description}, QText: {self.response.question.text()}, Response Voted: {self.response.text()}, Voter Username: {self.username}, Email: {self.email}"

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import time
import json
import os
import logging
import gammu

WEBHOOK_URL = os.getenv("WEBHOOK_URL")


def send_message(sender, text):
    payload = {"alias": sender, 'text': text}
    requests.post(WEBHOOK_URL, data=payload)


# function used to parse received sms
def loop_sms_receive():

    # process Received SMS
    all_sms = []
    start = True
    while True:
        try:
            if start:
                sms = gammu_sm.GetNextSMS(Folder=0, Start=True)
                start = False
            else:
                sms = gammu_sm.GetNextSMS(
                    Folder=0, Location=sms[0]['Location'])
            all_sms.append(sms)
        except gammu.ERR_EMPTY as e:
            break

    if not len(all_sms):
        return

    all_linked_sms = gammu.LinkSMS(all_sms)

    for sms in all_linked_sms:
        if sms[0]['UDH']['Type'] == 'NoUDH':
            message = {"datetime": str(
                sms[0]['DateTime']), "number": sms[0]['Number'], "text": sms[0]['Text']}
            payload = json.dumps(message, ensure_ascii=False)
            logging.info(payload)
            send_message(sms[0]['Number'], sms[0]['Text'])
            try:
                gammu_sm.DeleteSMS(Folder=0, Location=sms[0]['Location'])
            except Exception as e:
                logging.error(f'ERROR: Unable to delete SMS: {e}')
        elif sms[0]['UDH']['AllParts'] != -1:
            if len(sms) == sms[0]['UDH']['AllParts']:
                decoded_sms = gammu.DecodeSMS(sms)
                message = {"datetime": str(
                    sms[0]['DateTime']), "number": sms[0]['Number'], "text": decoded_sms['Entries'][0]['Buffer']}
                payload = json.dumps(message, ensure_ascii=False)
                logging.info(payload)
                send_message(sms[0]['Number'],
                             decoded_sms['Entries'][0]['Buffer'])
                for part in sms:
                    gammu_sm.DeleteSMS(Folder=0, Location=part['Location'])
            else:
                logging.info(
                    f"Incomplete Multipart SMS ({len(sms)}/{sms[0]['UDH']['AllParts']}): waiting for parts")
        else:
            logging.info(
                '***************** Unsupported SMS type *****************')
            logging.info('===============sms=================')
            logging.info(sms)
            logging.info('===============decoded_sms=================')
            decoded_sms = gammu.DecodeSMS(sms)
            logging.info(decoded_sms)
            logging.info('================================')
            gammu_sm.DeleteSMS(Folder=0, Location=sms[0]['Location'])


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s",
                        level=logging.INFO, datefmt="%H:%M:%S")

    pin = os.getenv("PIN")

    gammu_sm = gammu.StateMachine()
    gammu_sm.ReadConfig(Filename="/etc/gammu-smsdrc")
    gammu_sm.Init()

    if gammu_sm.GetSecurityStatus() == 'PIN':
        gammu_sm.EnterSecurityCode('PIN', pin)

    versionTuple = gammu.Version()
    logging.info(f'Gammu runtime: v{versionTuple[0]}')
    logging.info(f'Python-gammu runtime: v{versionTuple[1]}')
    logging.info(f'Manufacturer: {gammu_sm.GetManufacturer()}')
    logging.info(f'IMEI: {gammu_sm.GetIMEI()}')
    logging.info(f'SIMIMSI: {gammu_sm.GetSIMIMSI()}')

    logging.info('Gammu initialized')

    while True:
        time.sleep(1)
        loop_sms_receive()

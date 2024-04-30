from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_sqlalchemy import DBSessionMiddleware, db
from dotenv import load_dotenv
import os, random, logging, json, qrcode, requests
from sqlalchemy import create_engine
from sqlalchemy.sql import text

from jinja2 import Template, Environment, PackageLoader, select_autoescape
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

#print('os.environ', os.environ)

DATABASE_URL=os.getenv('DATABASE_URL', 'sqlite:///invoice.sqlite')
SECRET=os.getenv('SECRET')
DISCORD=os.getenv('DISCORD_WEBHOOK')
print('URL', DATABASE_URL, 'SECRET', SECRET, DISCORD)
engine = create_engine(DATABASE_URL, echo=True, isolation_level="AUTOCOMMIT", connect_args={'check_same_thread': False})
conn = engine.connect()

#template_str = open("templates/invoice.html", 'rb').read().decode("utf-8")
#template = Template(template_str)

if DISCORD:
    requests.post(DISCORD, json={"content":"Démarrage serveur Invoice !"})

def generateBill(no):
    dt,chk,cust_id = conn.execute(text("""SELECT dt,chk,customer FROM invoices WHERE no=:no;"""), {"no":no}).fetchall()[0]
    cust_name, cust_adr, cust_tel, cust_cat = conn.execute(text("""SELECT name,address,tel,cat FROM customer WHERE id=:id;"""), {"id":cust_id}).fetchall()[0]
    logging.info(f"generateBill({no}) : {dt} to {cust_name}")

    orders=conn.execute(text("""
    SELECT product, qty, name,price 
    FROM orders 
    JOIN products ON (orders.product=products.id) 
    WHERE invoice=:no;"""), {"no":no}).fetchall()
    print('orders', orders)

    tot = 0.0
    products=[]
    for order in orders:
        pl = order[1] * order[3]
        products.append({"k":order[1], "price":order[3], "name":order[2], "pid":order[0], "tot": pl})
        tot += pl

    invoice={
        "no": no,
        "cust": cust_id,
        "cat": cust_cat,
        "chk": str(chk),
        "dt": dt,
        "name": cust_name,
        "adr": cust_adr.replace('\\n', '\n'),
        "phone": cust_tel,
        "products": products,
        "total": tot
    }
    return invoice

WHITE = (255, 255, 255, 255)
RED = (255, 0, 0, 128)
BLUE = (0, 0, 255, 255)
BLACK = (0, 0, 0, 255)
logo = Image.open("logo128x128.png")

def generatePNG(no, chk, fn):
    data = generateBill(no)
    print(f"generatePDF, {no}, {chk}, {fn}; data.chk={data['chk']} -> {chk!=data['chk']}")
    if chk!=data['chk']: return None

    print('INVOICE', data)


    font12 = ImageFont.truetype("Lato-Light.ttf", 12)
    font20 = ImageFont.truetype("Lato-Light.ttf", 20)
    font24 = ImageFont.truetype("Lato-Light.ttf", 24)
    #font = ImageFont.load("arial.pil")
    mono20 = ImageFont.truetype("FreeMono.ttf", 20)

    width, height=(850, 1100)
    image = Image.new('RGBA', (width, height), WHITE)
    draw = ImageDraw.Draw(image)

    qr = qrcode.make(f"INVOICE:{data['no']}\nDATE:{data['dt']}\nCUST:{data['cust']:05d}\nCAT:{data['cat']}", box_size=3)
    image.paste(qr, (550, 10))


    image.paste(logo, (700, 10))
    draw.text((20, 20), f"INVOICE {data['no']}", fill=BLACK, font=font24)
    draw.text((20, 50), f"Issue date {data['dt']}", fill=BLACK, font=font20)
    draw.text((20, 80), f"Bill to {data['name']}", fill=BLACK, font=font20)
    draw.text((20, 120), f"Address {data['adr']}", fill=BLACK, font=font12)

    for idx,prod in enumerate(data['products']):
        draw.text((40, 200+idx*20), f"{prod['name']}", fill=BLUE, font=font20)
        draw.text((500, 200+idx*20), f"{prod['k']:2} x {prod['price']:6.2f} Euro", fill=BLUE, font=mono20)
        pass
    draw.line((40, 220+idx*20, 800, 220+idx*20), fill=255)
    draw.text((40, 230+idx*20), f"TOTAL", fill=RED, font=font20)
    draw.text((500, 230+idx*20), f"    {data['total']:6.2f} Euro", fill=RED, font=mono20)

    image.save(fn, "png")

    return True

logging.basicConfig(filename='logger.txt', level=logging.DEBUG)
nos = conn.execute(text("""SELECT no FROM invoices ORDER BY no LIMIT 100;"""), {}).fetchall()
for no in nos:
    #generatePDF(no[0], "static/invoice.pdf")
    pass
logging.basicConfig(level=logging.INFO)


@app.get("/")
def get_root(request: Request, data: str=''):
    ''' Renvoi vers /invoices
    '''
    return RedirectResponse(f"/invoices")


@app.get("/invoices")
def get_invoices(request: Request, start_date: str=''):
    ''' Donne la liste des factures, par issue date, dans la limite de 1000 factures<br/>
        Si header accept contiens json : format JSON, sinon format HTML<br/>
        parametre 'start_date' permet de donner la date de début (par défaut 2019-01-01)
    '''
    where = f"dt>'{start_date}'" if start_date else "true"
    invoices = conn.execute(text(f"""SELECT no,dt,chk,voteup,votedown FROM invoices WHERE {where} AND dt< datetime() ORDER BY dt LIMIT 1000;"""), {})
    if 'accept' in request.headers and 'json' in request.headers['accept']:
        return {"invoices": [{"no":f"{x[0]}-{x[2]}", "dt":x[1], "votesUP":x[3], "votesDOWN":x[4]} for x in invoices]}
    else:
        html="<html><header><title>Factures</title></header><body><h2>Invoices</h2><ul>"
        for x in invoices:
            html+=f"""<li><a target='img' href='/invoices/{x[0]}-{x[2]}'>{x[0]}</a> {x[1]} {str(x[3])+'👍🏻' if x[3] else ''} {str(x[4])+'👎🏻' if x[4] else ''}</li>"""
        html+="</ul></body></html>"
        return HTMLResponse(content=html, status_code=200) # {"status": "OK"}

@app.get("/invoices/{noid}")
def get_invoice(request: Request, noid: str="", secret: str=''):
    '''
    Retourne la facture au format PNG à partir de son n° (obtenu par la liste)
    '''
    vals=noid.split('-')
    print(f"vals={vals}")

    if secret==SECRET and 'accept' in request.headers and 'json' in request.headers['accept'] :
        return generateBill(vals[0])

    fn = f"static/{noid}.png"
    if True or not os.path.exists(fn):
        res = generatePNG(vals[0], vals[-1], fn)
        if not res:
            if DISCORD:
                client_host = request.client.host
                requests.post(DISCORD, json={"content":f"Essai de récupération de facture invalid {noid}, client_host={client_host}"})
            raise HTTPException(status_code=403, detail=f"Invalid n° {noid}")
            #return f"Invalid n° {noid}"
    return RedirectResponse("/"+fn)

@app.get("/invoices/voteup/{noid}")
def get_up(request: Request, noid: str=""):
    '''
    Vote UP pour une facture<br/>
    Retourne le nombre de votes UP/DOWN
    '''
    vals=noid.split('-')
    print(f"vals={vals}")
    conn.execute(text("""UPDATE invoices SET voteup=voteup+1 WHERE no=:no;"""), {"no":vals[0]}) #.fetchall()
    x = conn.execute(text("""SELECT voteup,votedown FROM invoices WHERE no=:no;"""), {"no":vals[0]}).fetchall()[0]
    return {'votesUP': x[0], 'voteDOWN': x[1]}

@app.get("/invoices/votedown/{noid}")
def get_down(request: Request, noid: str=""):
    '''
    Vote DOWN pour une facture<br/>
    Retourne le nombre de votes UP/DOWN
    '''
    vals=noid.split('-')
    print(f"vals={vals}")
    conn.execute(text("""UPDATE invoices SET votedown=votedown+1 WHERE no=:no;"""), {"no":vals[0]}) #.fetchall()
    x = conn.execute(text("""SELECT voteup,votedown FROM invoices WHERE no=:no;"""), {"no":vals[0]}).fetchall()[0]
    return {'votesUP': x[0], 'voteDOWN': x[1]}


def finish():
    print("*** EXIT ***")
    if DISCORD:
        requests.post(DISCORD, json={"content":"Arrêt serveur Invoice !"})

import atexit
atexit.register(finish)
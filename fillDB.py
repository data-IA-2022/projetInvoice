#from faker import Faker
import random, datetime, math, faker
#from datetime import datetime, time

fake = faker.Faker(['it_IT', 'en_US', 'fr_FR'])
"""
1000 clients
2000 products
"""

print("""---------------------------------------
--DROP TABLE customer;
CREATE TABLE customer(
    id int PRIMARY KEY,
    name TEXT,
    address TEXT,
    tel TEXT,
    cat TEXT(1)
);
INSERT INTO customer VALUES(-1, 'NAME', 'ADDRESS', 'TEL', 'CAT')""")
for n in range(1000):
    adr = fake.address().replace('\n', '\\n')
    #adrb = bytes(adr, 'utf-8')
    #print(adrb)
    print(f""",({n}, "{fake.name()}", "{adr}", "{fake.phone_number()}", '{"ABBCCCCCCCCCCCCCCC"[n % 13]}')""")
print(";\n\n")


print("""---------------------------------------
--DROP TABLE products;
CREATE TABLE products(
    id int PRIMARY KEY,
    name TEXT,
    price float
);
INSERT INTO products VALUES(-1, '***', 0.0)""")
for n in range(2000):
    print(f",({n}, \"{fake.sentence(nb_words=4, variable_nb_words=False)}\", {int(random.random()*10000)/100})")
print(";\n\n")





print('''
--DROP TABLE invoices;
--DROP INDEX dt_idx;
CREATE TABLE invoices(
    no string PRIMARY KEY,
    dt DATE,
    chk INT,
    customer INT,
    voteup int,
    votedown int,
	CONSTRAINT invoice1_FK FOREIGN KEY (customer) REFERENCES customer("id")
);
--DROP TABLE orders;
CREATE TABLE orders(
    invoice string,
    product INT,
    qty INT,
	CONSTRAINT orders1_FK FOREIGN KEY (invoice) REFERENCES invoices("no"),
	CONSTRAINT orders2_FK FOREIGN KEY (product) REFERENCES products("id")
);
-- CREATE INDEX dt_idx ON invoices(dt);
--INSERT INTO invoices VALUES('FAC_2024_0001', '2024-01-01 10:50:24', 42);
''')

N=20 # 10000/365 = 28

#random.seed(42)

for year in range(2019, 2025):
    no=1
    for month in range(1, 13):
        print("INSERT INTO invoices VALUES")
        virg=False
        for day in range(1,32):
            try:
                t=random.randrange(60*24)
                dt=datetime.datetime(year, month, day, hour=t//60, minute=t%60) # , hour=1, minutes=1, second=0
                N=2+1*math.sin(math.pi*month*2/12)+random.randrange(2)
                if month==12:
                    N+=2 # dec
                    if day>20: N+=10
                if dt.weekday()>4: N+=2 # WE
                N=int(N)
                print('--', dt, N, dt.weekday())
                for n in range(N):
                    s1=random.randrange(1000)
                    s2=random.randrange(10000)
                    t=random.randrange(60*24)
                    dt=datetime.datetime(year, month, day, hour=t//60, minute=t%60) # , hour=1, minutes=1, second=0
                    #print(f"{',' if virg else ''}('FAC_{year}_{no:04}', '{dt}', '{s1*s2}', {s1}, {s2})")
                    print(f"{',' if virg else ''}('FAC_{year}_{no:04}', '{dt}', {s1*s2}, {random.randrange(1000)}, 0, 0)") # no dt chk cust
                    no+=1
                    virg=True
            except Exception as e:
                print('-- ***', e)
                pass
        print(";")

    print("\nINSERT INTO orders VALUES (-1, -1, 0) -- invoice product qty")
    for n in range(no):
        for i in range(random.randrange(1, 10)):
            print(f",('FAC_{year}_{n:04}', {random.randrange(2000)}, {random.randrange(1, 10)})")

    print(";\n")


print("CREATE INDEX dt_idx ON invoices(dt);")


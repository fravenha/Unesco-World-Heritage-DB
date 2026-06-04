import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
from flask import Flask, render_template, abort
import logging
import db

warnings.filterwarnings('ignore', category=FutureWarning)

APP = Flask(__name__)

# Página inicial
@APP.route('/')
def index():
    stats = {}
    stats = db.execute('''
    SELECT 
      (SELECT COUNT(*) FROM Sites) AS n_sites,
      (SELECT COUNT(*) FROM Regions) AS n_regions,
      (SELECT COUNT(*) FROM States) AS n_states,
      (SELECT COUNT(*) FROM Criterias) AS n_criteria,
      (SELECT COUNT(*) FROM Risks) AS n_risks,
      (SELECT COUNT(*) FROM Selections) AS n_selections
    ''').fetchone()
    logging.info(stats)
    return render_template('index.html', stats=stats)

# Rotas para Sites
@APP.route('/sites/')
def list_sites():
    sites = db.execute('''
    SELECT siteID, name, description, longitude, latitude
    FROM Sites
    ORDER BY name
    ''').fetchall()
    return render_template('site-list.html', sites=sites)

@APP.route('/sites/<int:id>/')
def get_site(id):
    site = db.execute('''
    SELECT siteID, name, description, longitude, latitude, area_hectares
    FROM Sites
    WHERE siteID = ?
    ''', [id]).fetchone()

    if not site:
        abort(404, f"Site ID {id} não existe.")

    regions = db.execute('''
    SELECT r.name 
    FROM Regions r
    JOIN States s ON r.regionID = s.regionID
    JOIN Sites_Combinations sc ON s.stateID = sc.stateID
    WHERE sc.siteID = ?
    ''', [id]).fetchall()

    criterias = db.execute('''
    SELECT c.sigla, c.description 
    FROM All_Criterias ac
    JOIN Criterias c ON ac.sigla = c.sigla
    WHERE ac.selectionID IN (
        SELECT selectionID FROM Selections WHERE siteID = ?
    )
    ''', [id]).fetchall()

    return render_template('site.html', site=site, regions=regions, criterias=criterias)

# Rotas para Regions
@APP.route('/regions/')
def list_regions():
    regions = db.execute('''
    SELECT regionID, name 
    FROM Regions
    ORDER BY name
    ''').fetchall()
    return render_template('region-list.html', regions=regions)

@APP.route('/regions/<int:id>/')
def get_region(id):
    region = db.execute('''
    SELECT regionID, name 
    FROM Regions 
    WHERE regionID = ?
    ''', [id]).fetchone()

    if not region:
        abort(404, f"Region ID {id} não existe.")

    states = db.execute('''
    SELECT stateID, name
    FROM States
    WHERE regionID = ?
    ''', [id]).fetchall()

    return render_template('region.html', region=region, states=states)

# Rotas para States
@APP.route('/states/')
def list_states():
    states = db.execute('''
    SELECT stateID, name, iso_code, udnp_code
    FROM States
    ORDER BY name
    ''').fetchall()
    return render_template('state-list.html', states=states)

@APP.route('/states/<int:id>/')
def get_state(id):
    state = db.execute('''
    SELECT stateID, name, iso_code, udnp_code
    FROM States
    WHERE stateID = ?
    ''', [id]).fetchone()

    if not state:
        abort(404, f"State ID {id} não existe.")

    sites = db.execute('''
    SELECT s.siteID, s.name
    FROM Sites_Combinations sc
    JOIN Sites s ON sc.siteID = s.siteID
    WHERE sc.stateID = ?
    ''', [id]).fetchall()

    return render_template('state.html', state=state, sites=sites)

# Rotas para Criterias
@APP.route('/criterias/')
def list_criterias():
    criterias = db.execute('''
    SELECT sigla, description
    FROM Criterias
    ORDER BY sigla
    ''').fetchall()
    return render_template('criteria-list.html', criterias=criterias)

# Rotas para Risks
@APP.route('/risks/')
def list_risks():
    risks = db.execute('''
    SELECT riskID, type, year, period_start, period_end
    FROM Risks
    ORDER BY riskID
    ''').fetchall()
    return render_template('risk-list.html', risks=risks)

# Rotas para Selections
@APP.route('/selections/')
def list_selections():
    selections = db.execute('''
    SELECT selectionID, siteID, year_inscribed, justification
    FROM Selections
    ORDER BY selectionID
    ''').fetchall()
    return render_template('selection-list.html', selections=selections)

# Pergunta 1: Lista os anos em que os patrimonios foram inscritos pela primeira vez
@APP.route('/questions/1/')
def list_heritage_sites():
    years = db.execute('''
    SELECT DISTINCT year_inscribed
    FROM Selections
    ORDER BY year_inscribed 
    ''').fetchall()
    return render_template('question1.html', years=years)

# Pergunta 2: Listar patrimônios de uma região específica
@APP.route('/questions/2/<region_name>/')
def heritage_sites_by_region(region_name):

    region_name = 'Europe and North America'

    sites = db.execute('''
        SELECT s.name, st.name as 'Country'
        FROM Sites s
        JOIN Sites_Combinations sc ON s.siteID = sc.siteID
        JOIN States st ON sc.stateID = st.stateID
        JOIN Regions r ON st.regionID = r.regionID
        WHERE r.name = ? 
        ORDER BY st.name
    ''', [region_name]).fetchall()
    if sites is None:
        abort(404, 'Não foi possível encontrar Sites.'.format(region_name))
    return render_template('question2.html', region_name=region_name, sites=sites)

# Pergunta 3: Mostrar todos os patrimonios que pertencem a mais que um país
@APP.route('/questions/3/')
def inscription_years():
    sites = db.execute('''
    SELECT s.name, COUNT(st.name) as 'Number of Countries'
    FROM Sites s
    JOIN Sites_Combinations sc on s.siteID = sc.siteID 
    JOIN States st on st.stateID = sc.stateID
    WHERE transboundary = 1
    GROUP BY s.name
    HAVING COUNT(st.name) > 1
    ''').fetchall()
    return render_template('question3.html', sites=sites)

# Pergunta 4: Critérios associados a um patrimônio
@APP.route('/questions/4/')
def criteria_by_site():
    sites = db.execute('''
        SELECT s.name, ss.criteria_txt
        FROM Sites s
        INNER JOIN Selections ss ON s.siteID = ss.siteID
    ''').fetchall()

    return render_template('question4.html', sites=sites)

# Pergunta 5: Critérios mais utilizados na classificação dos patrimônios
@APP.route('/questions/5/')
def most_used_criteria():
    criteria = db.execute('''
    SELECT c.sigla, c.description, COUNT(ac.sigla) AS num_sites
    FROM Criterias c
    INNER JOIN All_Criterias ac ON c.sigla = ac.sigla
    GROUP BY c.description
    ORDER BY num_sites DESC
    ''').fetchall()
    return render_template('question5.html', criteria=criteria)

# Pergunta 6: Listar Patrimónios que estavam em risco em qualquer altura 
@APP.route('/questions/6/')
def sites_in_risk_by_category():
    sites = db.execute('''
    SELECT DISTINCT s.name
    FROM Sites s
    JOIN Info_Risks ir ON s.siteID = ir.siteID
    JOIN Risks r ON ir.riskID = r.riskID
    ''').fetchall()
    return render_template('question6.html', sites=sites)

# Pergunta 7: Patrimônios com maior área por região
@APP.route('/questions/7/')
def largest_area_by_region():
    areas = db.execute('''
    SELECT Regions.name AS region_name, MAX(Sites.area_hectares) AS max_area
    FROM Regions
    INNER JOIN States ON Regions.regionID = States.regionID
    INNER JOIN Sites_Combinations ON States.stateID = Sites_Combinations.stateID
    INNER JOIN Sites ON Sites_Combinations.siteID = Sites.siteID
    GROUP BY Regions.name
    ''').fetchall()
    return render_template('question7.html', areas=areas)

# Pergunta 8: Patrimônios selecionados pelos mesmos critérios
@APP.route('/questions/8/')
def sites_with_common_criteria():
    common_sites = db.execute('''
    SELECT DISTINCT s1.name AS site_a, s2.name AS site_b
    FROM Selections sel1
    JOIN Selections sel2 ON sel1.criteria_txt = sel2.criteria_txt AND sel1.SiteID < sel2.SiteID
    JOIN Sites s1 ON sel1.SiteID = s1.SiteID
    JOIN Sites s2 ON sel2.SiteID = s2.SiteID
    ''').fetchall()
    return render_template('question8.html', common_sites=common_sites)

# Pergunta 9: Listar patrimônios que foram seleciondos em 2002
@APP.route('/questions/9/')
def sites_by_region_and_criteria():
    sites = db.execute('''
    SELECT s.name, rg.name as 'Region'
    FROM Sites s
    JOIN Sites_Combinations sc on s.siteID = sc.siteID
    JOIN States st on sc.stateID = st.stateID
    JOIN Regions rg on rg.regionID = st.regionID
    JOIN Info_Risks ir ON s.siteID = ir.siteID
    JOIN Risks r ON ir.riskID = r.riskID
    WHERE r.date_end = '2002' or r.year = '2002' or ( r.period_Start <= '2002' and '2002' <=r.period_End)
    ORDER BY rg.name
    ''').fetchall()
    return render_template('question9.html',sites=sites)

# Pergunta 10: Patrimônios que foram selecionados este ano 
@APP.route('/questions/10/')
def sites_with_most_criteria():
    sites = db.execute('''
    SELECT DISTINCT s.name
    FROM Sites s
    LEFT JOIN Selections ss ON s.siteID = ss.siteID
    LEFT JOIN Date_Combinations dc ON dc.selectionID = ss.selectionID
    LEFT JOIN Dates d ON dc.dateID = d.dateID
    WHERE ss.year_inscribed = 2024 OR d.year = 2024
    ''').fetchall()
    return render_template('question10.html', sites=sites)


if __name__ == '__main__':
    APP.run(debug=True)

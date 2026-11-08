import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

st.set_page_config(page_title='TeachAhead | ALS Support', page_icon='🎓', layout='wide', initial_sidebar_state='expanded')

PURPLE = '#6841b7'
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], [data-testid="stAppViewContainer"] {font-family:Inter,Arial,sans-serif;}
.stApp {background:linear-gradient(120deg,#fdfcff,#f8f5ff);color:#24184c;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#f3edff,#faf8ff);border-right:1px solid #e6ddfa;}
[data-testid="stSidebar"] .stRadio label {font-weight:550;}
.block-container {max-width:1420px;padding-top:1.2rem;padding-bottom:3rem;}
h1,h2,h3 {color:#251550;letter-spacing:-.035em;}
h1 {font-size:2.05rem!important;} h2 {font-size:1.55rem!important;} h3 {font-size:1.12rem!important;}
[data-testid='stMetricValue'] {font-size:1.45rem!important;overflow-wrap:anywhere;white-space:normal!important;}
[data-testid='stMetricLabel'] {font-size:.85rem!important;}
[data-testid="stMetric"] {background:#f1eaff;padding:14px;border:1px solid #e0d3fb;border-radius:14px;}
[data-testid="stMetricValue"] {color:#4b2497;}
.stButton button[kind="primary"], [data-testid="stFormSubmitButton"] button[kind="primary"] {background:#6841b7;border:1px solid #6841b7;color:white;border-radius:10px;font-weight:700;}
.stButton button {border-radius:10px;}
[data-testid="stVerticalBlockBorderWrapper"] {border-color:#e5dcf8!important;border-radius:17px!important;background:#fff;}
[data-testid="stAlert"] {border-radius:13px;}
.ta-hero {display:flex;align-items:center;justify-content:space-between;gap:18px;margin:0 0 18px;flex-wrap:wrap;}
.ta-hero h1 {margin:0;color:#22144a;font-size:2.15rem;}
.ta-hero p {margin:6px 0 0;color:#5f5777;font-size:.94rem;}
.ta-case {background:#f2edff;border:1px solid #dcd0fc;border-radius:13px;padding:12px 18px;font-size:.83rem;color:#36245d;}
.ta-case b {font-size:.94rem;}
.ta-title {background:#fff;border:1px solid #e4dbf8;border-radius:17px;padding:16px 20px;margin:6px 0 19px;}
.ta-title h2 {margin:0;font-size:1.55rem;}
.ta-title p {margin:5px 0 0;color:#665d7c;font-size:.9rem;}
.ta-card {border:1px solid #e4daf9;background:white;border-radius:16px;padding:18px 20px;margin:6px 0 15px;box-shadow:0 4px 15px rgba(67,35,129,.035);}
.ta-card h3 {margin:0 0 11px;color:#321b75;}
.ta-card p {margin:5px 0 8px;line-height:1.55;}
.ta-chip {display:inline-block;border-radius:8px;background:#eee5ff;color:#5b329e;font-size:.76rem;padding:4px 9px;font-weight:700;}
.ta-note {background:#f1ecfc;border:1px solid #e0d3fa;border-radius:13px;padding:12px 16px;color:#4d3c75;font-size:.85rem;line-height:1.55;margin-top:12px;}
.ta-plan {background:#f6f2ff;border:1px solid #e8dcff;border-radius:13px;padding:13px 16px;margin:10px 0;}
.ta-plan strong {color:#4d2395;}
.ta-small {color:#6e6681;font-size:.82rem;}
.ta-sidebar-brand {font-size:1.7rem;font-weight:800;color:#271650;line-height:1.1;}
.ta-sidebar-sub {font-size:.84rem;color:#62577c;margin:7px 0 20px;}
hr {border-color:#e8dff6;}
</style>''', unsafe_allow_html=True)

INITIAL = [{'Month':0,'ALSFRS-R':48,'Source':'Case history'}, {'Month':6,'ALSFRS-R':43,'Source':'Case history'}, {'Month':12,'ALSFRS-R':39,'Source':'Case history'}, {'Month':18,'ALSFRS-R':36,'Source':'Case history'}, {'Month':24,'ALSFRS-R':33,'Source':'Case history'}, {'Month':27,'ALSFRS-R':32,'Source':'Case history'}]
if 'clinical' not in st.session_state: st.session_state.clinical = INITIAL.copy()
if 'followups' not in st.session_state: st.session_state.followups = []
if 'patient_feedback' not in st.session_state: st.session_state.patient_feedback = []
if 'caregiver_feedback' not in st.session_state: st.session_state.caregiver_feedback = []

def reset_demo_data():
    """Restore the fictional Alex case without changing ML artifacts."""
    st.session_state.clinical = [record.copy() for record in INITIAL]
    st.session_state.followups = []
    st.session_state.patient_feedback = []
    st.session_state.caregiver_feedback = []
    st.session_state.reset_demo_confirm = False
    st.session_state.demo_reset_notice = True

with st.sidebar:
    st.markdown('<div class="ta-sidebar-brand">🎓 TeachAhead</div><div class="ta-sidebar-sub">Predicting Change,<br>Preserving Identity</div>', unsafe_allow_html=True)
    st.divider()
    page = st.radio('NAVIGATE', ['ALS Progression','Current Functional Status','Patient-Centred Planning','Feedback & Follow-Up'], label_visibility='collapsed')
    st.divider()
    st.markdown('<div class="ta-card"><b>🎯 Our Approach</b><p class="ta-small">Predict → Personalize<br>→ Monitor → Adapt</p></div>', unsafe_allow_html=True)
    st.caption('BioHacks 2026 · Working prototype')
    st.divider()
    st.markdown('**↩️ Demo Controls**')
    st.caption('Restore Alex’s original case data and clear saved demo entries. Team ML results stay unchanged.')
    st.checkbox('I want to reset the demo', key='reset_demo_confirm')
    st.button('↩️ Reset Demo', on_click=reset_demo_data,
              disabled=not st.session_state.reset_demo_confirm,
              use_container_width=True)
    if st.session_state.get('demo_reset_notice', False):
        st.success('Demo restored to the original Alex case.')
        st.session_state.demo_reset_notice = False

st.markdown('''<div class="ta-hero"><div><h1>Welcome to <span style="color:#6841b7">TeachAhead</span></h1><p>A personalized ALS support dashboard to help patients anticipate changes, plan ahead,<br>and continue the activities that matter most.</p></div><div class="ta-case"><b>👤 Case: Alex Chen</b><br>Age 47 &nbsp;|&nbsp; Biology Teacher &nbsp;|&nbsp; ALS</div></div>''', unsafe_allow_html=True)

def section(title, desc, icon):
    st.markdown(f'<div class="ta-title"><h2>{icon} &nbsp;{title}</h2><p>{desc}</p></div>', unsafe_allow_html=True)

def card(title, content):
    st.markdown(f'<div class="ta-card"><h3>{title}</h3>{content}</div>', unsafe_allow_html=True)

latest = sorted(st.session_state.clinical, key=lambda r:r['Month'])[-1]

if page == 'ALS Progression':
    section('ALS Progression', 'Alex’s observed history and the team’s separately evaluated progression model.', '📈')
    c1,c2,c3 = st.columns([1.15,1,1])
    with c1: st.metric('Latest observed ALSFRS-R', f"{latest['ALSFRS-R']} / 48", help='Recorded score, not an ML prediction')
    with c2: st.metric('Latest assessment month', f"{latest['Month']}")
    with c3: st.metric('Personal goal', 'Teaching in June')
    left,right = st.columns([1.65,1], gap='large')
    with left:
        with st.container(border=True):
            st.subheader('Observed ALSFRS-R Over Time')
            st.caption('Solid points = case history or entered follow-up measurements. No forecast is shown.')
            df = pd.DataFrame(st.session_state.clinical).sort_values('Month')
            line = alt.Chart(df).mark_line(point=alt.OverlayMarkDef(color=PURPLE, size=90),color=PURPLE,strokeWidth=3).encode(
                x=alt.X('Month:Q',title='Months since baseline',scale=alt.Scale(domain=[0,max(30,int(df['Month'].max())+3)])),
                y=alt.Y('ALSFRS-R:Q',title='ALSFRS-R (/48)',scale=alt.Scale(domain=[0,48])),
                tooltip=['Month:Q','ALSFRS-R:Q','Source:N']
            ).properties(height=345)
            st.altair_chart(line,width='stretch')
            st.caption('Original case history: months 0, 6, 12, 18, 24 and 27. Additional entries are user-supplied demo data.')
    with right:
        card('🧠 Team ML Model · v0.2', '<p><b>Dataset:</b> ALS Data #2 (1,822 patients)</p><p><b>Selected model:</b> Clinical Random Forest, 22 early clinical features</p><p><b>Prediction target:</b> signed dFRS, 0–40 scale points/month (months 3–12)</p><p><b>Evidence:</b> 625 historical evaluation records; calibrated intervals</p>')
        st.info('The model is evaluated on historical dataset patients. It does NOT predict Alex’s 48-point ALSFRS-R score or a date when he will lose an ability.')
    st.divider()
    st.subheader('🤖 Team Model · Historical Evaluation')
    st.caption('Real saved results from the team’s ClinicalRandomForest v0.2. The historical evaluation set was previously viewed during development; this is not external clinical validation.')
    import json
    data_root = Path(__file__).resolve().parent
    pred_path = data_root / 'historical_test_predictions.csv'
    summary_path = data_root / 'summary.json'
    if not pred_path.exists() or not summary_path.exists():
        st.error('Team model result files are missing. Keep historical_test_predictions.csv and summary.json beside this app.')
    else:
        try:
            team_summary = json.loads(summary_path.read_text(encoding='utf-8'))
            team_df = pd.read_csv(pred_path)
            model_key = 'ClinicalRandomForest'
            required = {'source_row_1based','actual_dFRS',model_key}
            if not required.issubset(team_df.columns):
                st.error('Team prediction CSV does not contain the expected patient and model columns.')
            else:
                team_df = team_df.dropna(subset=list(required)).copy()
                team_df['source_row_1based'] = team_df['source_row_1based'].astype(int)
                team_df = team_df.rename(columns={model_key:'predicted_dFRS'})
                metrics = team_summary['models'][model_key]['metrics']
                radius90 = float(team_summary['models'][model_key]['radii']['90'])
                coverage90 = float(team_summary['models'][model_key]['intervals']['90']['coverage'])
                k1,k2,k3,k4 = st.columns(4)
                k1.metric('Historical RMSE',f"{metrics['rmse']:.3f}")
                k2.metric('Historical MAE',f"{metrics['mae']:.3f}")
                k3.metric('Historical patients',f"{len(team_df):,}")
                k4.metric('90% interval coverage',f'{coverage90*100:.1f}%')
                st.caption(f"22 clinical features · {team_summary['rmse_reduction_percent']:.1f}% lower RMSE than constant-mean baseline · dFRS points/month, not ALSFRS-R /48")
                lo=float(min(team_df['actual_dFRS'].min(),team_df['predicted_dFRS'].min()))
                hi=float(max(team_df['actual_dFRS'].max(),team_df['predicted_dFRS'].max()))
                dots=alt.Chart(team_df).mark_circle(color=PURPLE,opacity=.36,size=52).encode(
                    x=alt.X('actual_dFRS:Q',title='Observed signed dFRS (points/month)',scale=alt.Scale(domain=[lo,hi])),
                    y=alt.Y('predicted_dFRS:Q',title='Predicted signed dFRS (points/month)',scale=alt.Scale(domain=[lo,hi])),
                    tooltip=[alt.Tooltip('source_row_1based:Q',title='Source row'),alt.Tooltip('actual_dFRS:Q',format='.3f'),alt.Tooltip('predicted_dFRS:Q',format='.3f')])
                diag=alt.Chart(pd.DataFrame({'x':[lo,hi],'y':[lo,hi]})).mark_line(color='#be3c69',strokeDash=[6,5],strokeWidth=2).encode(x='x:Q',y='y:Q')
                st.altair_chart((dots+diag).properties(height=340),width='stretch')
                st.caption('Purple = historical evaluation patient · dashed line = perfect agreement. Error values describe retrospective prediction, not clinical accuracy.')
                st.subheader('🔎 Explore a Historical Patient')
                st.caption('Choose a de-identified dataset record to inspect the team’s saved prediction and calibrated 90% interval. This is not Alex.')
                choices=team_df['source_row_1based'].tolist()
                chosen=st.selectbox('Historical dataset source row',choices,format_func=lambda n:f'Dataset #2 · row {n:04d}')
                selected=team_df.loc[team_df['source_row_1based'].eq(chosen)].iloc[0]
                estimate=float(selected['predicted_dFRS'])
                observed=float(selected['actual_dFRS'])
                p1,p2,p3=st.columns(3)
                p1.metric('Predicted dFRS',f'{estimate:+.3f} / month')
                p2.metric('Observed dFRS',f'{observed:+.3f} / month')
                p3.metric('90% prediction interval',f'{estimate-radius90:+.3f} to {estimate+radius90:+.3f}')
                interval_data=pd.DataFrame({'x':[estimate-radius90,estimate,estimate+radius90,observed], 'kind':['Lower bound','Prediction','Upper bound','Observed']})
                interval_line=alt.Chart(pd.DataFrame({'x':[estimate-radius90,estimate+radius90],'y':[0,0]})).mark_line(color='#a58ada',strokeWidth=12).encode(x='x:Q',y='y:Q')
                interval_points=alt.Chart(interval_data).mark_point(filled=True,size=130).encode(x=alt.X('x:Q',title='Signed dFRS (points/month)'),y=alt.value(0),color=alt.Color('kind:N',scale=alt.Scale(domain=['Lower bound','Prediction','Upper bound','Observed'],range=['#a58ada','#6841b7','#a58ada','#d78040'])),tooltip=['kind:N',alt.Tooltip('x:Q',format='.3f')])
                st.altair_chart((interval_line+interval_points).properties(height=110),width='stretch')
                st.caption('Prediction and interval endpoints are from the team’s saved historical results and calibration summary. The observed outcome is shown only for historical evaluation.')
                with st.expander('Run the saved trained model on this historical record (optional)'):
                    st.caption('This loads the actual supplied .joblib model and applies it to the matching 22 early features. It may require the team’s scikit-learn version.')
                    if st.button('Run model inference for selected row'):
                        try:
                            import joblib
                            source_path=data_root/'ALS.txt'
                            model_path=data_root/'ClinicalRandomForest.joblib'
                            if not source_path.exists() or not model_path.exists():
                                st.error('ALS.txt or ClinicalRandomForest.joblib is missing.')
                            else:
                                raw=pd.read_csv(source_path,sep=r'\s+')
                                feature_names=team_summary['clinical_features']
                                sample=raw.iloc[[chosen-1]][feature_names]
                                loaded=joblib.load(model_path)
                                model_value=float(loaded.predict(sample)[0])
                                st.success(f'Saved model output: {model_value:+.4f} dFRS/month · saved evaluation prediction: {estimate:+.4f}')
                        except Exception as exc:
                            st.error(f'Unable to run saved model in this environment: {exc}')
                with st.expander('Model scope and validation notes'):
                    st.write('Predictors: 22 clinical variables from the early 0–3 month window. Target: signed dFRS during months 3–12 on the original 0–40 functional scale. Development: 957 patients; calibration: 240; historical evaluation: 625.')
                    st.write('The 90% interval coverage is an empirical fraction of historical outcomes contained in intervals, not classification accuracy. These results have not been externally validated.')
        except Exception as exc:
            st.error(f'Could not read team ML results: {exc}')
    st.markdown('<div class="ta-note">ℹ️ <b>Clinical separation:</b> Alex’s observed ALSFRS-R /48 history above is a case example. The team model predicts signed dFRS on a different 0–40 scale for historical dataset patients. Follow-up form entries do not retrain or update the ML model.</div>',unsafe_allow_html=True)

elif page == 'Current Functional Status':
    section('Current Functional Status', 'Alex Chen’s observed abilities, challenges, and personal goal.', '📋')
    a,b = st.columns([1.35,1],gap='large')
    with a:
        card('👤 Alex Chen', '<p><b>Age:</b> 47 &nbsp; • &nbsp; <b>Occupation:</b> Biology teacher</p><p><b>Diagnosis:</b> ALS</p><p><span class="ta-chip">Personal Goal</span> &nbsp; Continue teaching in June</p>')
    with b:
        st.metric('ALSFRS-R (latest observed)',f"{latest['ALSFRS-R']} / 48")
        st.caption(f"Assessment at month {latest['Month']}; follow-up entries may be hypothetical for this demo.")
    x,y = st.columns(2,gap='large')
    with x:
        card('💬 Speech','<p><span class="ta-chip">Observed status</span></p><p>• Speech rate: <b>165 words/min</b> in the morning → <b>118 words/min</b> in the afternoon.</p><p>• Intelligibility: <b>98%</b> → <b>91%</b>.</p><p>• Communication becomes more effortful later in the day.</p>')
        card('🚶 Mobility & Fatigue','<p><span class="ta-chip">Observed status</span></p><p>• Right foot drop and progressive lower-limb weakness.</p><p>• History of falls; uses an ankle-foot orthosis.</p><p>• Standing and moving around the classroom are increasingly tiring.</p>')
    with y:
        card('✋ Hand Function','<p><span class="ta-chip">Observed status</span></p><p>• Progressive hand weakness and reduced grip strength.</p><p>• Difficulty sustaining a pinch.</p><p>• Handwriting becomes illegible after approximately <b>10 minutes</b>.</p>')
        card('🎯 Personal Goal & Respiratory Status','<p>Continue teaching and maintain his identity and sense of purpose with appropriate support.</p><p><b>Original case FVC:</b> sitting 76%; supine 61%.</p>')
    if st.session_state.followups:
        follow = st.session_state.followups[-1]
        st.info(f"Latest entered follow-up (month {follow['month']}): ALSFRS-R {follow['score']}/48; FVC {follow['fvc']}%. These are entered values, not verified case-history measurements.")
    st.markdown('<div class="ta-note">ℹ️ This page describes observed or entered clinical status, separate from any ML-generated progression prediction.</div>',unsafe_allow_html=True)

elif page == 'Patient-Centred Planning':
    section('Patient-Centred Planning','Explore support options based on challenges, goals, and preferences.','🤝')
    left,right=st.columns([1,1.85],gap='large')
    with left:
        with st.container(border=True):
            st.subheader('Main Challenge')
            challenge=st.radio('What is most difficult right now?', ['Speech difficulties','Handwriting difficulties','Mobility and fatigue'],label_visibility='collapsed')
        with st.container(border=True):
            st.subheader('Comfortable trying assistive tools?')
            willing=st.radio('Preference',['Yes','Not yet'],label_visibility='collapsed')
    with right:
        with st.container(border=True):
            st.subheader('📋 Your Personalized Plan')
            st.caption('Support options for Alex to continue teaching')
            if challenge=='Speech difficulties':
                if willing=='Yes':
                    title='Explore classroom voice amplification and speech-language support'
                    items=['Try a wearable or stationary microphone to reduce speaking effort.','Consult a speech-language pathologist (SLP) about classroom communication strategies.','Consider scheduling speaking-intensive activities earlier in the day.']
                else:
                    title='Explore low-pressure communication options first'
                    items=['Discuss concerns about microphones or other assistive tools without pressure.','Consult an SLP about pacing and communication strategies.','Consider shorter speaking segments and more written or digital classroom materials.']
                why='These options aim to reduce speaking effort while supporting Alex’s goal of continuing to teach.'
            elif challenge=='Handwriting difficulties':
                title='Reduce handwriting demands in the classroom'
                items=['Explore typing, prepared slides, or a digital whiteboard.','Discuss hand-function strategies with an occupational therapist (OT).','Consider sharing board-writing tasks or adjusting lesson materials.']
                if willing=='Not yet': items[0]='Begin with small changes such as pre-written notes or prepared slides.'
                why='These options may reduce fine-motor demands during teaching.'
            else:
                title='Adapt classroom mobility and fatigue demands'
                items=['Explore a stool, seated teaching, and planned rest breaks.','Discuss foot drop, falls, and orthosis fit with the clinical care team.','Consider arranging classroom materials to reduce unnecessary walking.']
                if willing=='Not yet': items[0]='Begin with low-effort adjustments such as planned breaks and seating.'
                why='These options may help conserve energy and reduce mobility demands.'
            st.markdown(f'<div class="ta-plan"><strong>💜 {title}</strong></div>',unsafe_allow_html=True)
            for item in items: st.markdown('✓ '+item)
            st.markdown(f'<div class="ta-plan"><strong>💡 Why this may help</strong><p>{why}</p></div>',unsafe_allow_html=True)
            st.info('This is rule-based planning support, not an ML recommendation or medical advice. Discuss changes with the healthcare team.')

else:
    section('Feedback & Follow-Up','Review what worked, record new assessments, and identify discussion points.','🔄')
    c1,c2=st.columns(2,gap='large')
    with c1:
        with st.container(border=True):
            st.subheader('🩺 Clinical Follow-Up')
            st.caption('Record new clinical measurements from a subsequent assessment. Keep separate from subjective feedback.')
            with st.form('clinical_form'):
                month=st.number_input('Month since baseline',min_value=28,max_value=240,value=max(30,int(latest['Month'])+1),step=1)
                score=st.number_input('New ALSFRS-R (/48)',min_value=0,max_value=48,value=30,step=1)
                fvc=st.number_input('Respiratory function — FVC (%)',min_value=0.0,max_value=150.0,value=75.0,step=1.0)
                arm=st.selectbox('Arm strength (MRC grade 0–5; example muscle)',list(range(6)),index=4)
                leg=st.selectbox('Leg strength (MRC grade 0–5; example muscle)',list(range(6)),index=4)
                notes=st.text_area('Clinical examination notes',placeholder='e.g., gait, swallowing, respiratory symptoms...')
                save_clinical=st.form_submit_button('💾 Save Clinical Data',type='primary',width='stretch')
            if save_clinical:
                st.session_state.clinical=[r for r in st.session_state.clinical if r['Month']!=month]
                st.session_state.clinical.append({'Month':month,'ALSFRS-R':score,'Source':'Entered follow-up (demo)'})
                st.session_state.followups.append({'month':month,'score':score,'fvc':fvc,'arm':arm,'leg':leg,'notes':notes})
                st.success('Clinical follow-up saved in this session. The observed graph and latest status are updated.')
    with c2:
        with st.container(border=True):
            st.subheader('💬 Patient Feedback')
            st.caption('Tell us about your experience with a support strategy.')
            with st.form('patient_form'):
                strategy=st.selectbox('Support strategy tried',['Classroom voice amplification (microphone)','Typing / digital whiteboard','Rest breaks / seating adjustments','Other'])
                helpful=st.radio('Was it helpful?',['Yes','Somewhat','No'],horizontal=True)
                comfort=st.radio('Comfort level',['Comfortable','Neutral','Uncomfortable'],horizontal=True)
                patient_notes=st.text_area('Patient feedback',placeholder='What worked? What was uncomfortable?')
                save_patient=st.form_submit_button('💾 Save Patient Feedback',type='primary',width='stretch')
            if save_patient:
                st.session_state.patient_feedback.append({'strategy':strategy,'helpful':helpful,'comfort':comfort,'notes':patient_notes})
                st.success('Patient feedback saved in this session.')
    c3,c4=st.columns(2,gap='large')
    with c3:
        with st.container(border=True):
            st.subheader('👥 Caregiver Observation')
            st.caption('Optional observations, with the patient’s consent.')
            with st.form('caregiver_form'):
                changes=st.multiselect('What changes did you observe?',['Increased fatigue','More difficulty speaking','Greater mobility difficulty','Other'])
                caregiver_notes=st.text_area('Notes (frequency, situation, severity)',placeholder='e.g., Needed to repeat himself in the afternoon...')
                save_caregiver=st.form_submit_button('💾 Save Observation',width='stretch')
            if save_caregiver:
                st.session_state.caregiver_feedback.append({'changes':changes,'notes':caregiver_notes})
                st.success('Caregiver observation saved in this session.')
    with c4:
        with st.container(border=True):
            st.subheader('📋 Plan Review')
            st.caption('Discussion prompts based on recorded information, not automatic clinical recommendations.')
            if st.session_state.patient_feedback:
                feedback=st.session_state.patient_feedback[-1]
                if feedback['helpful']=='Yes' and feedback['comfort']=='Comfortable':
                    st.success('Continue: Discuss whether the strategy remains useful and comfortable.')
                elif feedback['helpful']=='No' or feedback['comfort']=='Uncomfortable':
                    st.warning('Adjust: Discuss alternatives and barriers with the care team.')
                else: st.info('Adjust: Consider changes that may improve comfort or usefulness.')
            else: st.info('Enter patient feedback to see a tailored plan review prompt.')
            if st.session_state.caregiver_feedback:
                obs=st.session_state.caregiver_feedback[-1]
                if obs['changes']: st.write('**Caregiver-reported changes:** '+', '.join(obs['changes']))
            if st.session_state.followups:
                follow=st.session_state.followups[-1]
                st.write(f"**New clinical assessment recorded:** month {follow['month']}, ALSFRS-R {follow['score']}/48, FVC {follow['fvc']}%.")
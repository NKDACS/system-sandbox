# maching learning module and relevant utilities
import pandas as pd
import numpy as np
from joblib import load
from django.db import connection, transaction
from django.db.models.fields.files import FieldFile
from django.db.models import CharField
from django.db.models.functions import Concat
from .models import Resume, ResumeResult
from .utils import logger


def transform() -> pd.DataFrame:
    """
    Transform Resume ORM to pandas dataframe
    Do all the feature pre-processing stuff
    """
    sql = str(Resume.objects.filter(submitted=True).query)
    data = pd.read_sql(sql, connection, index_col='id')
    return data


def predict_score(model_file: FieldFile) -> pd.DataFrame:
    """
    load scoring model and predict
    """
    model = load(model_file)
    data = transform()
    for i in data.itertuples():
        try:
            score = model.predict(np.array(i[1:]).reshape(1,-1))
            data.loc[i[0], ['score', 'error']] = score, pd.NA
        except Exception as e:
            data.loc[i[0], ['score', 'error']] = -1.0, e.__str__()
    data['rank'] = data['score'].rank(method='min', na_option='bottom')
    return data[['score', 'error', 'rank']]


def predict_rank():
    """
    load ranker model and predict
    """
    pass


def _update_by_item(x) -> ResumeResult:
    """
    Apply function
    """
    x['obj'].score = x['score']
    x['obj'].rank = x['rank']
    return x['obj']


def write_change(result: pd.DataFrame) -> None:
    """
    write changes to ResumeResult ORM
    use transaction to secure atomic
    """
    for key in ['score', 'rank']:
        if key not in result.columns:
            raise KeyError(f'Incomplete result dataframe: {key} not found')
    with transaction.atomic():
        result.sort_index(inplace=True)
        result['obj'] = ResumeResult.objects\
            .filter(resume__submitted=True).order_by('id')
        result['obj'] = result.apply(_update_by_item, axis=1)
        ResumeResult.objects.bulk_update(result['obj'], ['score', 'rank'], batch_size=256)
    

def get_error(result: pd.DataFrame) -> list:
    """
    Return error information in a list
    """
    result[['name','person_id']] = Resume.objects\
        .filter(id__in=result.index)\
        .order_by('id').annotate(
            total_name=Concat('student__last_name', 'student__first_name', output_field=CharField())
        ).values_list('total_name', 'student__person_id')
    result['id'] = result.index
    feedback = result[['id', 'name','person_id','error']]
    feedback.dropna(inplace=True)
    return feedback.to_dict('records')
  

from sklearn.base import BaseEstimator
class RM(BaseEstimator):
    def __init__(self):
        super(RM, self).__init__()
    
    def fit(self,features:np.ndarray,target:np.ndarray,sample_weight:np.ndarray=None):
        return self
    
    def predict(self,features:np.ndarray):
        return np.random.rand(len(features))

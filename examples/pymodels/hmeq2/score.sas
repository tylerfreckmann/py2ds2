ds2_options sas;
package pyscore / overwrite=yes;
    dcl package pymas py;
    dcl double pystop;
    dcl package logger logr('App.tk.MAS');

    method score(
         double "LOAN"
        ,  double "MORTDUE"
        ,  double "VALUE"
        ,  varchar "REASON"
        ,  varchar "JOB"
        ,  double "YOJ"
        ,  double "DEROG"
        ,  double "DELINQ"
        ,  double "CLAGE"
        ,  double "NINQ"
        ,  double "CLNO"
        ,  double "DEBTINC"
        , in_out double "EM_EVENTPROBABILITY"
    );
        dcl nvarchar(10485760) pypgm;
        dcl double rc;
        if null(py) and pystop ^= 1 then do;
            py = _new_ pymas();
            rc = py.appendSrcLine('from sklearn.externals import joblib');
            rc = py.appendSrcLine('import pandas as pd');
            rc = py.appendSrcLine('');
            rc = py.appendSrcLine('ml_pipe = joblib.load(''/pymodels/hmeq2/ml_pipe.pickle'')');
            rc = py.appendSrcLine('');
            rc = py.appendSrcLine('def score(LOAN, MORTDUE, VALUE, REASON, JOB, YOJ, DEROG, DELINQ, CLAGE, NINQ, CLNO, DEBTINC):');
            rc = py.appendSrcLine('    ''Output: EM_EVENTPROBABILITY''');
            rc = py.appendSrcLine('    data = pd.DataFrame([{''LOAN'': LOAN, ''MORTDUE'': MORTDUE, ''VALUE'': VALUE, ''REASON'': REASON, ''JOB'': JOB, ''YOJ'': YOJ, ''DEROG'': DEROG, ''DELINQ'': DELINQ, ''CLAGE'': CLAGE, ''NINQ'': NINQ, ''CLNO'': CLNO, ''DEBTINC'': DEBTINC}])');
            rc = py.appendSrcLine('    _, EM_EVENTPROBABILITY = ml_pipe.predict_proba(data)[0]');
            rc = py.appendSrcLine('    return float(EM_EVENTPROBABILITY)');
            pypgm = py.getSource();
            revision = py.publish(pypgm, 'pyscore');
            if revision < 1 then do;
                pystop = 1;
                logr.log( 'e', 'publish revision=$s', revision );
                return;
            end;
            rc = py.useMethod('score');
            if rc then do;
                pystop = 1;
                logr.log( 'e', 'useMethod rc=$s', rc );
                return;
            end;
        end;
        if pystop ^= 1 then do;
            rc = py.setDouble('LOAN', LOAN);
            if rc then do;
                logr.log('e', 'set LOAN rc=$s', rc);
                return;
            end;
            rc = py.setDouble('MORTDUE', MORTDUE);
            if rc then do;
                logr.log('e', 'set MORTDUE rc=$s', rc);
                return;
            end;
            rc = py.setDouble('VALUE', VALUE);
            if rc then do;
                logr.log('e', 'set VALUE rc=$s', rc);
                return;
            end;
            rc = py.setString('REASON', REASON);
            if rc then do;
                logr.log('e', 'set REASON rc=$s', rc);
                return;
            end;
            rc = py.setString('JOB', JOB);
            if rc then do;
                logr.log('e', 'set JOB rc=$s', rc);
                return;
            end;
            rc = py.setDouble('YOJ', YOJ);
            if rc then do;
                logr.log('e', 'set YOJ rc=$s', rc);
                return;
            end;
            rc = py.setDouble('DEROG', DEROG);
            if rc then do;
                logr.log('e', 'set DEROG rc=$s', rc);
                return;
            end;
            rc = py.setDouble('DELINQ', DELINQ);
            if rc then do;
                logr.log('e', 'set DELINQ rc=$s', rc);
                return;
            end;
            rc = py.setDouble('CLAGE', CLAGE);
            if rc then do;
                logr.log('e', 'set CLAGE rc=$s', rc);
                return;
            end;
            rc = py.setDouble('NINQ', NINQ);
            if rc then do;
                logr.log('e', 'set NINQ rc=$s', rc);
                return;
            end;
            rc = py.setDouble('CLNO', CLNO);
            if rc then do;
                logr.log('e', 'set CLNO rc=$s', rc);
                return;
            end;
            rc = py.setDouble('DEBTINC', DEBTINC);
            if rc then do;
                logr.log('e', 'set DEBTINC rc=$s', rc);
                return;
            end;
            rc = py.execute();
            logr.log('d', 'execute rc=$s', rc);
            EM_EVENTPROBABILITY = py.getDouble('EM_EVENTPROBABILITY');
        end;
    end;
endpackage;

"""
Compute binary classification metrics
"""

def compute_validation_acc(model,features_test,target):
    predict_proba=model.predict_proba(features_test)
    predicted=model.predict(features_test)
    pred_prob=np.array(predict_proba[:,1])
    area_under_curve =  roc_auc_score(target,pred_prob)
    labels=['has-not-clicked','clicked']
    print("accuracy score:",accuracy_score(target,model.predict(features_test)))
    print(target.shape,np.sum(predicted))
    cm=confusion_matrix(target,predicted)
    
    sns.set(rc={'figure.figsize':(18,5)})
    fig, ax=plt.subplots(1,3)
    fig.suptitle("Metrics for binary classification", fontsize=16)
    
    #confusion matrix
    akws = {"ha": 'center',"va": 'center',"size": 17}
    sns.heatmap(cm, annot=True, fmt="d", linewidths=.5,ax=ax[0],annot_kws=akws); #annot=True to annotate cells
    ax[0].set_xlabel('Predicted labels')
    ax[0].set_ylabel('True labels'); 
    ax[0].set_title('Confusion Matrix') 
    ax[0].xaxis.set_ticklabels(labels)
    ax[0].yaxis.set_ticklabels(labels)
    
    #ROC
    fpr, tpr, _ = metrics.roc_curve(target,  pred_prob)
    ax[1].plot(fpr,tpr,label=f"auc = {area_under_curve:.3f}")
    ax[1].set_xlabel('True positive rate')
    ax[1].set_title('ROC curve')
    ax[1].set_ylabel('False positive rate')
    ax[1].legend(loc="lower right")
    
    #precision recall
    precision, recall, thresholds = precision_recall_curve(target, pred_prob)
    f1 = f1_score(target, predicted)
    auc_pr = auc(recall, precision)
    ap = average_precision_score(target, pred_prob)
    print('f1=%.3f auc_pr=%.3f avg_pr=%.3f auc=%.3f' % (f1, auc_pr, ap,area_under_curve))
    
    ax[2].plot(precision,recall,label=f"auc_pr = {auc_pr:.3f}")
    ax[2].set_title('PR Curve')
    ax[2].set_xlabel('Recall')
    ax[2].set_ylabel('Precision')
    ax[2].legend(loc="upper right")
    fig.tight_layout()
    fig.subplots_adjust(top=0.95)
    #plt.show()

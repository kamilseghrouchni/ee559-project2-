import math
import torch
import matplotlib.pyplot as plt


def load_data(plotting=False):
    '''
    Generate toy dataset for training and test sets
    Dataset are 1000 points generated uniformly on [0, 1]
    Corresponding label is 1 if the point is inside the disk of radius sqrt(1/2*pi), 0 otherwise

    Attributes
    -------
    plotting
        If true, plots dataset, before standardization

    Returns
    -------
    tensor
        Standardized training examples
    trainY
        Training targets
    tensor
        Standardized test examples
    testY
        Test targets
    '''
    
    N = 1000 # Number of points to generate
    r2 = 1/(2*math.pi)
    trainX = torch.FloatTensor(N, 2).uniform_(0, 1)
    testX = torch.FloatTensor(N, 2).uniform_(0, 1)
    center = torch.FloatTensor([0.5, 0.5]) # Center of the disk
    trainY = to_one_hot((trainX.sub(center).pow(2).sum(axis=1) < r2).long())
    testY = to_one_hot((testX.sub(center).pow(2).sum(axis=1) < r2).long())

    mean_ = trainX.mean()
    std_ = trainX.std()

    if plotting:
        plot_dataset(trainX, trainY, 'train')
        plot_dataset(testX, testY, 'test')

    return standardize(trainX, mean_, std_), trainY, standardize(testX, mean_, std_), testY

def to_one_hot(y):
    '''
    One-hot encoding of vector y
    '''
    Y = torch.zeros((len(y), len(y.unique())))

    Y[range(len(y)), y] = 1

    return Y

def standardize(x, mean, std):
    '''
    Standardize data 'x' with mean and std
    '''
    return x.sub_(mean).div_(std)

def plot_dataset(data, labels, name):
    '''
    Plot dataset, coloured with corresponding labels
    '''
    plt.scatter(data[:,0], data[:,1], c=['r' if p==0 else 'b' for p in labels.argmax(1)])
    #plt.show()

    fname = 'fig/' + name + '.png'

    print(f'Plot of {name} data saved under {fname} \n')

    plt.savefig(fname)

def train_visualization(net, losses, testX, testY):
    '''
    Generation of training plots

    1: training loss over time
    2: Correlation matrix (of test predictions)
    3: Plot scattering of test predictions

    Attributes
    -------
    net
        Trained network
    losses
        Collected losses at each epoch
    testX
        Test dataset
    testY
        Test targets
    '''
    # Plot losses
    plt.figure()

    plt.plot(range(1,len(losses)+1), losses, 'k--')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.grid()
    loss_fname = 'fig/loss.png'
    print(f'Plot of training loss saved under {loss_fname}')
    plt.savefig(loss_fname)

    # Get test predictions for future plots
    pred = net(testX).argmax(1)

    b00 = (pred == 0) & (testY.argmax(1) == 0) # Predicted as 0 and true class is 0
    b01 = (pred == 0) & (testY.argmax(1) == 1) # Predicted as 0 and true class is 1
    b10 = (pred == 1) & (testY.argmax(1) == 0) # Predicted as 1 and true class is 0
    b11 = (pred == 1) & (testY.argmax(1) == 1) # Predicted as 1 and true class is 1

    # Plot confusion matrix
    plt.figure()
    conf = torch.tensor([[b00.sum(), b10.sum()], [b01.sum(), b11.sum()]])
    plt.matshow(conf, cmap='tab10')

    for i in range(conf.shape[0]):
        for j in range(conf.shape[1]):
            plt.text(i, j, '{:d}'.format(conf[i,j]), ha='center', va='center')

    plt.xlabel('True Class')
    plt.ylabel('Predicted class')
    #plt.show()
    conf_fname = 'fig/confmat.png'
    print(f'Plot of confusion matrix saved under {conf_fname}')
    plt.savefig(conf_fname)

    # Plotting scattering of correctly (resp. falsely) predicted values
    plt.figure()
    correct0 = torch.nonzero(b00==True)
    correct1 = torch.nonzero(b11==True)
    plt.scatter(testX[correct0,0], testX[correct0, 1], c='r', alpha=0.2, label='class 0')
    plt.scatter(testX[correct1,0], testX[correct1, 1], c='b', alpha=0.2, label='class 1')
    errors = torch.cat((torch.nonzero(b01==True), torch.nonzero(b10 == True)), dim=0)
    plt.scatter(testX[errors,0], testX[errors, 1], c='k', label='errors')
    plt.legend()
    #plt.show()
    pred_fname = 'fig/predictions.png'
    print(f'Plot of test predictions saved under {pred_fname}')
    plt.savefig(pred_fname)

# DemosPython
The deep learning project is on object detection for detecting traffic signs using the fast.ai (version 0.7) library. The techniques taught by Jeremy Howard were very helpful and the fast.ai library is a breeze to use. I find that 3 papers are very useful for learning Object detection using DL from scratch.

1) Redmon, Joseph, Santosh Divvala, Ross Girshick, and Ali Farhadi. "You only look once: Unified, real-time object detection." In Proceedings of the IEEE conference on computer vision and pattern recognition, pp. 779-788. 2016.
2) Liu W, Anguelov D, Erhan D, Szegedy C, Reed S, Fu CY, Berg AC. SSD: Single shot multibox detector. In European conference on computer vision 2016 Oct 8 (pp. 21-37). Springer, Cham.
3) Lin TY, Goyal P, Girshick R, He K, Dollár P. Focal loss for dense object detection. arXiv preprint arXiv:1708.02002. 2017 Aug 7.

The technique implemented is Focal loss and the SSD paper as taught by Jeremy Howard in his lesson on Object detection.

## Dataset
The dataset is the awesome traffic signs data provided by Telenav. The links to download the train and test data can be found in the Github repo  https://github.com/Telenav/Telenav.AI

## Results
![alt-text](https://github.com/abhinavsunderrajan/DemsoPython/blob/master/MAP.png)
The mean average precision on different traffic signs.

![alt-text](https://github.com/abhinavsunderrajan/DemsoPython/blob/master/GT1.png)
Example 1

![alt-text](https://github.com/abhinavsunderrajan/DemsoPython/blob/master/GT2.png)
Example 2

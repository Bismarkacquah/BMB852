# Week 1 Assignment - Demonstrating Basic Unix Commands

### Samtools Version

Before using the 'samtools' command, you must first activate the bioinfo environment by typing 'bioinfo'

Then, when you type 'samtools' into the terminal, a large response will pop up containing the samtools program version followed by a long list of commands

My samtools version shows up as follows:

```bash
Program: samtools (Tools for alignments in the SAM format)
Version: 1.24 (using htslib 1.24)
```

## Commands Needed to Create A Nested Directory

Start by listing your directories using the 'ls' command:

```bash
ls
```

This will list all your directories and files in your current directory:

```bash
edirect  edu  snap  snpcall.2026.mk  work
```

As you can see, my directories currently consist of edirect, edu, snap, snpcall.2026.mk, and work. We are mainly going to be focusing on the 'work' directory. 

Next, change your directory using the 'cd' command. I am going to change my directory to 'work' Here is how this is entered:

```bash
cd work
```

Notice how the new directory is shown next to the user on the next line after switching the directory. This helps the user keep track of where they are working. This shows up for me as:

```bash
laurenmags@Leaftop ~/work
$
```

Next, since this is week one, we are going to make a new directory underneath the 'work' directory:

```bash
mkdir week1
```

Now when we do the ls command (within the 'work' directory!) the directories within the 'work' directory will be displayed, including our new 'week1' directory

```bash
laurenmags@Leaftop ~/work
$ ls
snpcall  week1
```
Now we have created a directory within a directory! 

## Creating and Manipulating a File

Using the same steps shown before, we are going to move into the week1 directory:

```bash
cd week1
```

Now, we are going to create a file two different ways. First, we are going to create an empty file using the 'touch' command:

```bash
touch test.txt
```

You can confirm that the file has been created with the 'ls' command

Second, the other way to create a file is by directly putting information into a new file. I will demonstrate this with the 'date' command. The 'date' command typically outputs the date, pretty intuitive, but as you will see with the '>' tool, the output will be dumped into the created file:

```bash
date > date.txt
```

You can read this file by using the 'head' command:

```bash
head date.txt
```

Which prints the date:

```bash
Thu Aug 27 13:08:16 EDT 2026
```

From here, we can copy or move a file into a separate directory as well:

Moving:

```bash
 mv date.txt testdir
```

Copying:

```bash
cp test.txt testdir
```

Use the "ls" command to ensure that the files have moved and copied as intended. 

## Accessing a File Quickly from your Home Directory

Now let's zoom out a bit from where we are. To give yourself some perspective of your location, use the 'pwd' command to print your working directory, or your current location.

```bash
pwd
```

This prints for me as:

```bash
/home/laurenmags/work/week1
```

The ~ symbol represents your home directory, so let's navigate back there using the 'cd' command. 

You can do this the long way:

```bash
cd /home/laurenmags/
```

Or the short way:

```bash
cd ~
```

Since we have created many new directories and files now, let's install and use the 'tree' command to get a visual map of what our navigation options are. To add the tree command, start by activating your bioinfo environment with 'bioinfo', then enter 'pixi add tree'. Now you can use the tree command. To avoid clutter, I am going to make a tree specifically for my 'work' directory:

```bash
tree work
```

This prints:

```bash
    work
    ├── snpcall
    │   ├── Makefile
    │   ├── adapter.fa
    │   ├── bam
    │   │   ├── SRR1553425-AF086833.bam
    │   │   └── SRR1553425-AF086833.bam.bai
    │   ├── fastq
    │   │   ├── SRR1553425_1.fastq
    │   │   ├── SRR1553425_1P.fq
    │   │   ├── SRR1553425_1U.fq
    │   │   ├── SRR1553425_2.fastq
    │   │   ├── SRR1553425_2P.fq
    │   │   └── SRR1553425_2U.fq
    │   ├── refs
    │   │   ├── AF086833.fa
    │   │   ├── AF086833.fa.amb
    │   │   ├── AF086833.fa.ann
    │   │   ├── AF086833.fa.bwt
    │   │   ├── AF086833.fa.fai
    │   │   ├── AF086833.fa.pac
    │   │   ├── AF086833.fa.sa
    │   │   └── AF086833.gff
    │   ├── snpcall.2026.mk
    │   └── vcf
    │       ├── SRR1553425-AF086833.vcf.gz
    │       └── SRR1553425-AF086833.vcf.gz.csi
    ├── week1
    │   ├── README.md
    │   ├── test.txt
    │   └── testdir
    │       ├── date.txt
    │       └── test.txt
    └── week2
    
    9 directories, 25 files
```
Now we can easily look at the path to get to a file, such as the 'test.txt' file. 

To instantly change to the directory that contains the 'test.txt' file, we can enter the following path after the 'cd' command:

```bash
cd ~/work/week1/testdir/
```

Now the files are right there and can be accessed easily. You can even open them in the terminal using the 'less' command. Press 'Q' to exit the viewer. 

A more roundabout way of navigating to the file can also be done as such:

```bash
cd ~
    
cd work
    
cd week1
    
cd testdir
```

This navigates step by step, changing directories individually. This allows you to better visualize where you are, but takes longer. 





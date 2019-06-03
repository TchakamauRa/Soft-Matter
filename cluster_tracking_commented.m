avi_fname = '9Vpp_3.avi'; %starts with one particualr avi file
d = 15;  %approximate particle diameter in pixel
bound_lower=180;
obj=VideoReader(avi_fname); %
N_frames=get(obj,'numberOfFrames'); %gets length of that specific avi
ia_0=read(obj,1);
ia=ia_0;
%%
%bkg=zeros(size(ia_0,1),size(ia_0,2));
%get rid of background

for i=1:1000
   im=read(obj,i);
   bkg=bkg+double(im);
end
bkg=bkg/1000;
%%

    str=sprintf('9Vpp_%d',fname); %keep a string around for the ___ with the amplitude adn filename aached
    avi_fname=sprintf('9Vpp_%d.avi',fname); %string around the amplitude and filename atached --- name of the avi file in folder
    d = 15;  %approximate particle diameter in pixel
    bound_lower=180;   % set threshold
    obj=VideoReader(avi_fname);  %use the VideoReader to read named avi file; makes object
    N_frames=get(obj,'numberOfFrames');  % get list of all frames in the object above; uses keyword 'numberOfFrames' to get this
    ia_0=read(obj,1); %ia_0 is the frist frame of the video
    ia=ia_0; %initialize variable ia to the first frame
    cluster_config=zeros(N_frames,3); % array N_frames long, fileld with triplets of zero
    %thresh=zeros(size(ia,1),size(ia,2),N_frames);
    for k=1:N_frames  
        ia=read(obj,k); %nth frame
        iac=imadjust(ia(:,:)); %imadjust does... something...
        BW=imbinarize(iac,0.4); % this black and white converson - use 0.4 as the threshold
        cc=bwconncomp(BW); % get connected components, of a binary image
        %keep only the largest connected structure
        numpix=cellfun(@numel,cc.PixelIdxList); % number of elements for each of the clusters in cc; the decorator might be evaluated spearately only ach tiem a sructure is called
        if numpix>0 % kind of clumsy way to elminate all but largest cluster??
            idx=find(numpix<max(numpix)); %find all clusters smaller than the larges (why we need the number of pizels)
            cluster_config(k,1)=max(numpix); %set the first column, in every row, equal to the number of pixels of the largest cluster
            for i=idx
                BW(cc.PixelIdxList{i})=0; % delete the pixels which ae smaller than the max == set their pixels to 0 in their frames
            end
            %get properties of largest connected cluster
            stats=regionprops(BW,'orientation','eccentricity');
            %stats=regionprops(BW,'orientation','centroid');
            %cluster_config(k,2:3)=stats.Centroid;
            cluster_config(k,2)=stats.Eccentricity;
            cluster_config(k,3)=stats.Orientation;
            %cluster_config(k,4)=stats.MajorAxisLength;
            %cluster_config(k,5)=stats.MinorAxisLength;
        end
        if mod(k,10000) == 0
            avi_fname
            k
        end
        %thresh(:,:,k)=BW;
    end
    
    %process data to get state level information
for fname=30:40 % frame names??
    str=sprintf('9Vpp_%d',fname); %print the frme number
    load(str) %wait, no, load the frame number
    numpix=[0;cluster_config(:,1)>550;0]; %thisholds....... [0, whether there was a full cluster or not in the frame, and 0]???
    lvls=cluster_config(:,2);
    pct=[0;lvls;0];
    pct_f=zeros(size(numpix));
    p_int=[]; %pentagons/hexagons
    c_int=[]; %chevrons
    t_int=[]; %triangles
    plevel=[0.8 1]; % range [of eccentricity] for pentagon/hexagon
    clevel=[0.7 0.5]; % range of values in which it is chevron
    tlevel=[0 0.45]; % range of values in which it is triangle
    %only look at transitions when a particle comes off and reattaches
    br=find(diff(numpix));  % diff is the vector contining differences in pixel numbers from fame toframe, and br = find(diff) is the vector containing a label for 
							% each place there was a pixel difference 
    for s=1:length(br)-1
        seg=pct(br(s):br(s+1)); % segment of video
        if numpix(br(s+1))
            %average over eccentricity to get a cleaner signal
            av=mean(seg);
            %determine p/c/t
            p=(av>min(plevel)&av<max(plevel)); % boolean
            c=(av>min(clevel)&av<max(clevel)); % boolean
            t=(av>min(tlevel)&av<max(tlevel)); % boolean
            pct_f(br(s):br(s+1))=p*mean(plevel)+c*mean(clevel)+t*mean(tlevel);
            p_int=[p_int;p*length(seg)];
            c_int=[c_int;c*length(seg)];
            t_int=[t_int;t*length(seg)];
        end
        
        %old code
        %     tr=pct;
        %     p=(tr>min(plevel)&tr<max(plevel));
        %     c=(tr>min(clevel)&tr<max(clevel));
        %     t=(tr>min(tlevel)&tr<max(tlevel));
        %     pct_f=p*mean(plevel)+c*mean(clevel)+t*mean(tlevel);
        %     startPosp = find(diff([p(1)-1, p']));
        %     lengthsp = diff([startPosp, numel(p)+1]);
        %     valuesp = p(startPosp);
        %     p_on=lengthsp(valuesp==1);
        %     startPosc=find(diff([c(1)-1,c']));
        %     lengthsc=diff([startPosc, numel(c)+1]);
        %     valuesc=c(startPosc);
        %     c_on=lengthsc(valuesc==1);
        %     startPost=find(diff([t(1)-1,t']));
        %     lengthst=diff([startPost, numel(t)+1]);
        %     valuest=t(startPost);
        %     t_on=lengthst(valuest==1);
        %     p_int=[p_int,p_on];
        %     t_int=[t_int,t_on];
        %     c_int=[c_int,c_on];
    end
    p_int=p_int(p_int>0);
    c_int=c_int(c_int>0);
    t_int=t_int(t_int>0);
    
    tr=zeros(3,3);
    
    tr_pc=0;
    tr_pt=0;
    tr_pp=0;
    tr_cc=0;
    tr_ct=0;
    tr_cp=0;
    tr_tc=0;
    tr_tt=0;
    tr_tp=0;
    for i=1:length(pct_f(1,:))
        data=pct_f(1:end,i);
        c=find(diff(data)); %find transitions
        %assemble state vector
        svz=data(c-1);
        ini=find(svz>0);
        sv=svz(ini);
        for j=2:length(sv)-1
            orig=round(sv(j-1),1);
            dest=round(sv(j),1);
            if orig==0.9&&dest==0.9
                tr_pp=tr_pp+1;
                tr(1,1)=tr(1,1)+1;
            elseif orig==0.9&&dest==0.6
                tr_pc=tr_pc+1;
                tr(2,1)=tr(2,1)+1;
            elseif orig==0.9&&dest==0.2
                tr_pt=tr_pt+1;
                tr(3,1)=tr(3,1)+1;
            elseif orig==0.6&&dest==0.9
                tr_cp=tr_cp+1;
                tr(1,2)=tr(1,2)+1;
            elseif orig==0.6&&dest==0.6
                tr_cc=tr_cc+1;
                tr(2,2)=tr(2,2)+1;
            elseif orig==0.6&&dest==0.2
                tr_ct=tr_ct+1;
                tr(3,2)=tr(3,2)+1;
            elseif orig==0.2&&dest==0.9
                tr_tp=tr_tp+1;
                tr(1,3)=tr(1,3)+1;
            elseif orig==0.2&&dest==0.6
                tr_tc=tr_tc+1;
                tr(2,3)=tr(2,3)+1;
            elseif orig==0.2&&dest==0.2
                tr_tt=tr_tt+1;
                tr(3,3)=tr(3,3)+1;
            end
        end
    end
    save(str)
    
    str
end
%%
t_tot=[];
p_tot=[];
c_tot=[];
tr_tot=zeros(3,3);
nfr=0;
for i=1:30
    load(sprintf('9Vpp_%d',i),'t_int','c_int','p_int','tr','N_frames')
    t_tot=[t_tot;t_int];
    c_tot=[c_tot;c_int];
    p_tot=[p_tot;p_int];
    tr_tot=tr_tot+tr;
    nfr=nfr+N_frames;
end
%%
%exclude data with no clusters
%written for 2-particle unit, 2017-09-15

thresh2=160;
nparts=[200;200;0;0;0;cluster_config(:,1);0;0]>thresh2;
theta_r=cluster_config(:,3);
w=pulsewidth(nparts*1,1:N_frames+7);
s=[pulsesep(nparts*1,1:N_frames+7);0];
rots={};
idx=1;
j=1;

for i=1:length(w)
    br=w(i);
    rf=s(i);
    if br>10
        rots{j,1}=theta_r(idx:idx+br-1);
        [pks,loc]=findpeaks(rots{j,1});
        rots{j,3}=theta_r(idx:idx+br-1);
        for pk=1:length(loc)
            ind=loc(pk);
            rots{j,3}=[rots{j,3}(1:ind);rots{j,3}(ind+1:end)+180];
        end
        rots{j,2}=diff(smooth(hampel(rots{j,1})));
        rots{j,4}=diff(smooth(hampel(rots{j,3},10),30));
        j=j+1;
    end
    idx=idx+br+rf;
end

%%
 figure(1)
 cla
cmap=winter;
%dtheta=[];
%fcw=[];
%maxr=[];
hold on
 for i=1:length(rots)
     if length(rots{i,1})<10000
    plot(smooth(hampel(rots{i,4}(1:end-2)),20)*pi/180+i,'color',cmap(i*2,:),'linewidth',2)
     end
    %shrots=smooth(hampel(rots{i,4}(1:end-1)));
    %maxr=[maxr,shrots(end-1)*pi/180];
    %dtheta=[dtheta;smooth(hampel(rots{i,4}(1:end-1))*pi/180,20)];
     %tra=smooth(rots{i,2}(1:end-1),20);
     %fcw(i)=nnz(tra>0)/(nnz(tra>0)+nnz(tra<0));
 end
 maxr=maxr';

%   for i=1:length(rots2)
%     plot(rots2{i,1}(1:end-1)*pi/180)
%      %dtheta=[dtheta;smooth(rots{i,2}(1:end-1),20)];
%      %tra=smooth(rots{i,2}(1:end-1),20);
%      %fcw(i)=nnz(tra>0)/(nnz(tra>0)+nnz(tra<0));
%   end
%   for i=1:length(rots3)
%     plot(rots3{i,1}(1:end-1)*pi/180)
%      %dtheta=[dtheta;smooth(rots{i,2}(1:end-1),20)];
%      %tra=smooth(rots{i,2}(1:end-1),20);
%      %fcw(i)=nnz(tra>0)/(nnz(tra>0)+nnz(tra<0));
%   end
%   for i=1:length(rots4)
%     plot(rots4{i,1}(1:end-1)*pi/180)
%      %dtheta=[dtheta;smooth(rots{i,2}(1:end-1),20)];
%      %tra=smooth(rots{i,2}(1:end-1),20);
%      %fcw(i)=nnz(tra>0)/(nnz(tra>0)+nnz(tra<0));
%  end
% for j=1:8
%     plot(smooth(rots2{j,2}(1:end-1),20)*pi/180)
% end
%set(gca,'YScale','log')
%set(gca,'XScale','log')
%box on
%axis([0 1E4 5E-3 1E4])

%%
%identify floppy mode/hingelike transitions
for fname=31:30
    str=sprintf('9Vpp_%d',fname);
    load(str)
    numpix=[0;cluster_config(:,1)>520;0];
    lvls=cluster_config(:,2);
    pct=[0;lvls;0];
    hinge={};
    floppy=[];
    %only look at transitions when a particle comes off and reattaches
    br=find(diff(numpix));
    ct=1;
    plevel=[0.8 1];
    clevel=[0.7 0.5];
    tlevel=[0 0.45];
    for s=1:length(br)-1
        seg=pct(br(s):br(s+1));
        if numpix(br(s+1))
            stat=smooth(seg,100);
            hinge{ct}=smooth(seg,100);
            p=nnz(stat>min(plevel)&stat<max(plevel));
            c=nnz(stat>min(clevel)&stat<max(clevel));
            t=nnz(stat>min(tlevel)&stat<max(tlevel));
            floppy(ct,1)=p;
            floppy(ct,2)=c;
            floppy(ct,3)=t;
            ct=ct+1;
        end
    end
    floppy=floppy>1+0;
    floppy(:,4)=(floppy(:,1)+floppy(:,2)+floppy(:,3))>1;
    defhinge=nnz(floppy(:,4));
    save(str)
    str
end

%%

t_tot=[];
p_tot=[];
c_tot=[];
tr_tot=zeros(3,3);
nfr=0;
dhinge=0;
for i=1:40
    load(sprintf('9Vpp_%d',i),'t_int','c_int','p_int','tr','N_frames','defhinge')
    t_tot=[t_tot;t_int];
    c_tot=[c_tot;c_int];
    p_tot=[p_tot;p_int];
    tr_tot=tr_tot+tr;
    nfr=nfr+N_frames;
    dhinge=defhinge+dhinge;
end
length(p_tot)/length([c_tot;p_tot;t_tot])

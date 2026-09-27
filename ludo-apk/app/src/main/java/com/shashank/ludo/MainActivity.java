package com.shashank.ludo;

import android.app.Activity;
import android.os.Bundle;
import android.graphics.*;
import android.graphics.drawable.ColorDrawable;
import android.view.*;
import android.content.Context;
import android.os.Vibrator;
import java.util.*;

public class MainActivity extends Activity {
    @Override public void onCreate(Bundle b) {
        super.onCreate(b);
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN, WindowManager.LayoutParams.FLAG_FULLSCREEN);
        getWindow().setNavigationBarColor(Color.rgb(3,18,48));
        setContentView(new LudoView(this));
    }
}

class LudoView extends View {
    // Board order: top=red, right=green, bottom=yellow, left=blue.
    static final int RED=0, GREEN=1, YELLOW=2, BLUE=3;
    final int[] COLORS={Color.rgb(239,68,68),Color.rgb(34,197,94),Color.rgb(250,204,21),Color.rgb(14,165,233)};
    final int[] DARK={Color.rgb(185,28,28),Color.rgb(21,128,61),Color.rgb(161,98,7),Color.rgb(3,105,161)};
    final String[] NAMES={"RED","GREEN","YELLOW","BLUE"};

    // 52-cell outer route, matching the supplied classic Ludo layout.
    final int[][] route={
        {6,0},{7,0},{8,0},{8,1},{8,2},{8,3},{8,4},{8,5},
        {9,6},{10,6},{11,6},{12,6},{13,6},{14,6},{14,7},{14,8},
        {13,8},{12,8},{11,8},{10,8},{9,8},{8,9},{8,10},{8,11},
        {8,12},{8,13},{8,14},{7,14},{6,14},{6,13},{6,12},{6,11},
        {6,10},{6,9},{5,8},{4,8},{3,8},{2,8},{1,8},{0,8},
        {0,7},{0,6},{1,6},{2,6},{3,6},{4,6},{5,6},{6,5},
        {6,4},{6,3},{6,2},{6,1}
    };
    final int[][][] homeLane={
        {{7,1},{7,2},{7,3},{7,4},{7,5},{7,6}},
        {{13,7},{12,7},{11,7},{10,7},{9,7},{8,7}},
        {{7,13},{7,12},{7,11},{7,10},{7,9},{7,8}},
        {{1,7},{2,7},{3,7},{4,7},{5,7},{6,7}}
    };
    final int[] startIndex={0,13,26,39};
    final boolean[] safe={true,false,false,false,false,false,false,true,
                          false,false,false,false,false,true,false,true,
                          false,false,false,false,false,false,false,false,
                          false,false,true,false,false,false,false,false,
                          false,false,false,false,false,false,false,true,
                          false,true,false,false,false,false,false,false,
                          false,false,false,false,false};
    final Random rng=new Random();

    int players=2, turn=0, dice=0;
    boolean rolled=false, gameOver=false;
    int[][] token=new int[4][4]; // -1 home, 0..56 moving, 57 finished
    Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
    RectF boardRect=new RectF();
    float cell=1f, boardLeft=0, boardTop=0;
    float density;
    String message="RED: Roll the dice";
    long lastRollAt=0;

    public LudoView(Context c){
        super(c);
        density=getResources().getDisplayMetrics().density;
        p.setTypeface(Typeface.create("sans",Typeface.BOLD));
        setLayerType(View.LAYER_TYPE_SOFTWARE,null);
        reset();
    }

    void reset(){
        for(int a=0;a<4;a++) Arrays.fill(token[a],-1);
        turn=0; dice=0; rolled=false; gameOver=false;
        message=NAMES[turn]+": Roll the dice";
        invalidate();
    }

    @Override protected void onDraw(Canvas c){
        super.onDraw(c);
        float w=getWidth(), h=getHeight();
        drawBlueBackground(c,w,h);

        float side=118*density;
        float size=Math.min(h-24*density, w-2*side-24*density);
        boardLeft=(w-size)/2f; boardTop=(h-size)/2f; cell=size/15f;
        boardRect.set(boardLeft,boardTop,boardLeft+size,boardTop+size);

        drawSidePanel(c,RED,0,side-10*density);
        drawSidePanel(c,YELLOW,w-side+10*density,side-10*density);
        drawBoard(c);
        drawTokens(c);
        drawTurnOverlay(c,w,h);
    }

    void drawBlueBackground(Canvas c,float w,float h){
        c.drawColor(Color.rgb(5,49,115));
        p.setStyle(Paint.Style.FILL);
        for(float y=0;y<h;y+=34*density){
            for(float x=0;x<w;x+=34*density){
                int ix=(int)(x/(34*density)), iy=(int)(y/(34*density));
                p.setColor(((ix+iy)&1)==0?Color.rgb(8,61,135):Color.rgb(6,54,123));
                c.drawRect(x,y,x+34*density,y+34*density,p);
            }
        }
        p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(1.2f); p.setColor(Color.argb(80,255,255,255));
        for(float y=8*density;y<h;y+=68*density) for(float x=8*density;x<w;x+=68*density){
            c.drawCircle(x,y,15*density,p);
            c.drawCircle(x+8*density,y+8*density,5*density,p);
        }
    }

    void fill(Canvas c,int color,float l,float t,float r,float b){
        p.setStyle(Paint.Style.FILL); p.setColor(color); c.drawRect(l,t,r,b,p);
    }
    void stroke(Canvas c,int color,float width,float l,float t,float r,float b){
        p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(width); p.setColor(color); c.drawRect(l,t,r,b,p);
    }
    float X(float gx){return boardLeft+gx*cell;}
    float Y(float gy){return boardTop+gy*cell;}

    void drawBoard(Canvas c){
        // Outer board / four colored homes.
        fill(c,Color.WHITE,boardLeft,boardTop,boardLeft+15*cell,boardTop+15*cell);
        fill(c,COLORS[RED],X(0),Y(0),X(6),Y(6));
        fill(c,COLORS[GREEN],X(9),Y(0),X(15),Y(6));
        fill(c,COLORS[YELLOW],X(9),Y(9),X(15),Y(15));
        fill(c,COLORS[BLUE],X(0),Y(9),X(6),Y(15));

        drawHome(c,RED,0,0);
        drawHome(c,GREEN,9,0);
        drawHome(c,YELLOW,9,9);
        drawHome(c,BLUE,0,9);

        // Grid cells: paint outer route and home lanes.
        for(int i=0;i<52;i++){
            int gx=route[i][0], gy=route[i][1];
            int col=Color.WHITE;
            for(int q=0;q<4;q++) if(i==startIndex[q]) col=COLORS[q];
            fill(c,col,X(gx),Y(gy),X(gx+1),Y(gy+1));
            stroke(c,Color.rgb(148,163,184),1.2f,X(gx),Y(gy),X(gx+1),Y(gy+1));
            if(safe[i]){
                p.setStyle(Paint.Style.FILL); p.setColor(Color.argb(42,15,23,42));
                c.drawCircle(X(gx)+cell/2,Y(gy)+cell/2,cell*.22f,p);
            }
        }
        for(int q=0;q<4;q++){
            for(int k=0;k<6;k++){
                int gx=homeLane[q][k][0], gy=homeLane[q][k][1];
                fill(c,Color.WHITE,X(gx),Y(gy),X(gx+1),Y(gy+1));
                if(k==5) fill(c,COLORS[q],X(gx),Y(gy),X(gx+1),Y(gy+1));
                stroke(c,Color.rgb(148,163,184),1.2f,X(gx),Y(gy),X(gx+1),Y(gy+1));
            }
        }
        // Center four triangles.
        float cx=X(7.5f), cy=Y(7.5f);
        Path path=new Path();
        int[] qs={RED,GREEN,YELLOW,BLUE};
        float[][] pts={{X(6),Y(6),X(9),Y(6),cx,cy},
                       {X(9),Y(6),X(9),Y(9),cx,cy},
                       {X(9),Y(9),X(6),Y(9),cx,cy},
                       {X(6),Y(9),X(6),Y(6),cx,cy}};
        for(int q=0;q<4;q++){
            path.reset(); path.moveTo(pts[q][0],pts[q][1]); path.lineTo(pts[q][2],pts[q][3]); path.lineTo(pts[q][4],pts[q][5]); path.close();
            p.setStyle(Paint.Style.FILL); p.setColor(COLORS[qs[q]]); c.drawPath(path,p);
            p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(1.4f); p.setColor(Color.rgb(71,85,105)); c.drawPath(path,p);
        }
        // Subtle border.
        stroke(c,Color.rgb(30,41,59),3f,boardLeft,boardTop,boardLeft+15*cell,boardTop+15*cell);
    }

    void drawHome(Canvas c,int q,int gx,int gy){
        float l=X(gx)+cell*.75f, t=Y(gy)+cell*.75f, r=X(gx+6)-cell*.75f, b=Y(gy+6)-cell*.75f;
        p.setShadowLayer(8,0,4,Color.argb(75,0,0,0));
        fill(c,Color.WHITE,l,t,r,b);
        p.clearShadowLayer();
        float[][] pos={{.32f,.32f},{.68f,.32f},{.32f,.68f},{.68f,.68f}};
        for(int i=0;i<4;i++){
            p.setStyle(Paint.Style.FILL); p.setColor(COLORS[q]);
            c.drawCircle(l+(r-l)*pos[i][0],t+(b-t)*pos[i][1],cell*.58f,p);
            p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(2); p.setColor(Color.argb(90,15,23,42));
            c.drawCircle(l+(r-l)*pos[i][0],t+(b-t)*pos[i][1],cell*.58f,p);
        }
    }

    void drawTokens(Canvas c){
        for(int q=0;q<players;q++){
            for(int t=0;t<4;t++){
                float[] pos=tokenPosition(q,t);
                boolean selectable=rolled && q==turn && legal(q,t,dice) && !gameOver;
                p.setStyle(Paint.Style.FILL);
                p.setColor(COLORS[q]);
                p.setShadowLayer(selectable?12:5,0,3,Color.argb(150,0,0,0));
                c.drawCircle(pos[0],pos[1],cell*.34f,p);
                p.clearShadowLayer();
                p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(selectable?4:2); p.setColor(Color.WHITE);
                c.drawCircle(pos[0],pos[1],cell*.34f,p);
                if(selectable){
                    p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(2); p.setColor(Color.WHITE);
                    c.drawCircle(pos[0],pos[1],cell*.48f,p);
                }
                p.setStyle(Paint.Style.FILL); p.setColor(Color.WHITE);
                p.setTextSize(cell*.22f); p.setTextAlign(Paint.Align.CENTER);
                c.drawText(String.valueOf(t+1),pos[0],pos[1]+cell*.08f,p);
            }
        }
    }

    float[] tokenPosition(int q,int t){
        int prog=token[q][t];
        if(prog==-1){
            float[][] home={{1.8f,1.8f},{10.8f,1.8f},{10.8f,10.8f},{1.8f,10.8f}};
            float bx=home[q][0], by=home[q][1];
            float[][] off={{0f,0f},{2.4f,0f},{0f,2.4f},{2.4f,2.4f}};
            return new float[]{X(bx+off[t][0]),Y(by+off[t][1])};
        }
        if(prog<52){
            int idx=(startIndex[q]+prog)%52;
            return new float[]{X(route[idx][0])+.5f*cell,Y(route[idx][1])+.5f*cell};
        }
        if(prog<57){
            int k=prog-52;
            return new float[]{X(homeLane[q][k][0])+.5f*cell,Y(homeLane[q][k][1])+.5f*cell};
        }
        return new float[]{X(7)+cell,Y(7)+cell};
    }

    void drawSidePanel(Canvas c,int q,float left,float width){
        float h=getHeight();
        boolean active=(turn==q);
        float top=h*.17f, bottom=h*.83f;
        p.setStyle(Paint.Style.FILL);
        p.setColor(Color.argb(active?235:175,255,255,255));
        c.drawRoundRect(left,top,left+width,bottom,18*density,18*density,p);
        p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(active?3:1.5f);
        p.setColor(COLORS[q]); c.drawRoundRect(left,top,left+width,bottom,18*density,18*density,p);

        p.setStyle(Paint.Style.FILL); p.setColor(COLORS[q]);
        c.drawRoundRect(left+8*density,top+8*density,left+width-8*density,top+54*density,12*density,12*density,p);
        p.setColor(Color.WHITE); p.setTextAlign(Paint.Align.CENTER); p.setTextSize(13*density);
        c.drawText(q==RED?"Player 1":"Player 2",left+width/2,top+37*density,p);

        float cy=top+108*density;
        p.setStyle(Paint.Style.FILL); p.setColor(Color.WHITE);
        p.setShadowLayer(5,0,2,Color.argb(100,0,0,0));
        c.drawRoundRect(left+18*density,cy-28*density,left+width-18*density,cy+28*density,12*density,12*density,p);
        p.clearShadowLayer();
        drawDie(c,left+width/2,cy,q==turn?dice:0);

        float by=cy+82*density;
        p.setStyle(Paint.Style.FILL); p.setColor(COLORS[q]);
        c.drawRoundRect(left+14*density,by-22*density,left+width-14*density,by+22*density,14*density,14*density,p);
        p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(2); p.setColor(Color.WHITE);
        c.drawCircle(left+width/2,by,13*density,p);
        p.setStyle(Paint.Style.FILL); p.setColor(Color.WHITE);
        p.setTextSize(11*density); c.drawText("●",left+width/2,by+4*density,p);

        p.setTextSize(11*density); p.setColor(Color.WHITE);
        String status=gameOver?(q==turn?"WINNER":""):active?(rolled?"MOVE TOKEN":"YOUR TURN"):"WAIT";
        c.drawText(status,left+width/2,bottom-18*density,p);
    }

    void drawTurnOverlay(Canvas c,float w,float h){
        float y=h-22*density;
        p.setStyle(Paint.Style.FILL);
        p.setColor(Color.argb(205,0,25,70));
        c.drawRoundRect(w/2-125*density,y-24*density,w/2+125*density,y+6*density,15*density,15*density,p);
        p.setColor(Color.WHITE); p.setTextAlign(Paint.Align.CENTER); p.setTextSize(12*density);
        c.drawText(gameOver?message:(rolled?"Tap a highlighted token":message),w/2,y-4*density,p);
    }

    void drawDie(Canvas c,float cx,float cy,int n){
        if(n<=0) { p.setStyle(Paint.Style.FILL); p.setColor(Color.rgb(30,41,59)); p.setTextAlign(Paint.Align.CENTER); p.setTextSize(20*density); c.drawText("?",cx,cy+7*density,p); return; }
        p.setColor(Color.rgb(30,41,59)); p.setStyle(Paint.Style.FILL);
        float r=7*density;
        float[][] dots={{-.23f,-.23f},{.23f,-.23f},{0,0},{-.23f,.23f},{.23f,.23f},{-.23f,0},{.23f,0}};
        int[] map={0,1,2,3,4,5,6};
        boolean[] use=new boolean[7];
        if(n==1) use[2]=true;
        if(n==2){use[0]=true;use[4]=true;}
        if(n==3){use[0]=true;use[2]=true;use[4]=true;}
        if(n==4){use[0]=true;use[1]=true;use[3]=true;use[4]=true;}
        if(n==5){use[0]=true;use[1]=true;use[2]=true;use[3]=true;use[4]=true;}
        if(n==6){use[0]=true;use[1]=true;use[3]=true;use[4]=true;use[5]=true;use[6]=true;}
        for(int i=0;i<7;i++) if(use[i]) c.drawCircle(cx+dots[i][0]*cell*1.8f,cy+dots[i][1]*cell*1.8f,r,p);
    }

    boolean legal(int q,int t,int d){
        int prog=token[q][t];
        if(prog==57) return false;
        if(prog==-1) return d==6;
        return prog+d<=57;
    }

    boolean hasLegal(int q,int d){
        for(int t=0;t<4;t++) if(legal(q,t,d)) return true;
        return false;
    }

    void roll(){
        if(gameOver) { reset(); return; }
        if(rolled) return;
        dice=1+rng.nextInt(6); rolled=true; lastRollAt=System.currentTimeMillis();
        vibrate();
        if(!hasLegal(turn,dice)){
            message=NAMES[turn]+": no legal move";
            invalidate();
            postDelayed(()->{
                rolled=false;
                if(dice!=6) nextTurn(); else message=NAMES[turn]+": roll again (6)";
                invalidate();
            },650);
            return;
        }
        int count=0, only=-1;
        for(int t=0;t<4;t++) if(legal(turn,t,dice)){count++;only=t;}
        message=NAMES[turn]+": choose a token";
        invalidate();
        if(count==1){ final int selected=only; postDelayed(()->moveToken(selected),300); }
    }

    void moveToken(int t){
        if(!rolled || gameOver || !legal(turn,t,dice)) return;
        int d=dice;
        if(token[turn][t]==-1) token[turn][t]=0;
        else token[turn][t]+=d;
        capture(turn,t);
        boolean finishedAll=true;
        for(int k=0;k<4;k++) if(token[turn][k]!=57) finishedAll=false;
        if(finishedAll){
            gameOver=true; rolled=false;
            message=NAMES[turn]+" wins! Tap NEW GAME";
            vibrate();
            invalidate(); return;
        }
        rolled=false;
        if(d==6){
            message=NAMES[turn]+": roll again";
        } else {
            nextTurn();
        }
        invalidate();
    }

    void capture(int q,int t){
        int prog=token[q][t];
        if(prog<0 || prog>=52) return;
        int idx=(startIndex[q]+prog)%52;
        if(safe[idx]) return;
        for(int oq=0;oq<players;oq++){
            if(oq==q) continue;
            for(int ot=0;ot<4;ot++){
                int op=token[oq][ot];
                if(op<0 || op>=52) continue;
                int oi=(startIndex[oq]+op)%52;
                if(oi==idx) token[oq][ot]=-1;
            }
        }
    }

    void nextTurn(){
        turn=(turn+1)%players;
        message=NAMES[turn]+": Roll the dice";
    }

    void vibrate(){
        try{
            Vibrator v=(Vibrator)getContext().getSystemService(Context.VIBRATOR_SERVICE);
            if(v!=null) v.vibrate(35);
        }catch(Exception ignored){}
    }

    @Override public boolean onTouchEvent(android.view.MotionEvent e){
        if(e.getAction()!=MotionEvent.ACTION_UP) return true;
        float x=e.getX(), y=e.getY();
        float w=getWidth(), h=getHeight();
        float side=118*density;

        if(turn==RED && x<side && y>h*.20f && y<h*.70f){ roll(); return true; }
        if(turn==YELLOW && x>w-side && y>h*.20f && y<h*.70f){ roll(); return true; }

        if(rolled && !gameOver){
            for(int t=0;t<4;t++){
                if(!legal(turn,t,dice)) continue;
                float[] pos=tokenPosition(turn,t);
                if(Math.hypot(x-pos[0],y-pos[1])<cell*.72f){
                    moveToken(t); return true;
                }
            }
        }
        if(gameOver){
            reset(); return true;
        }
        return true;
    }

}

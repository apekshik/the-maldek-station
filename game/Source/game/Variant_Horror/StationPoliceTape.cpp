#include "StationPoliceTape.h"
#include "Sound/SoundBase.h"
#include "Sound/SoundAttenuation.h"
#include "Components/SceneComponent.h"
#include "Components/SplineMeshComponent.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/Character.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInstanceDynamic.h"

AStationPoliceTape::AStationPoliceTape()
{
 PrimaryActorTick.bCanEverTick=true;
 SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("TapeRoot")));
}
void AStationPoliceTape::OnConstruction(const FTransform& T){Super::OnConstruction(T);Build();}
void AStationPoliceTape::PostRegisterAllComponents(){Super::PostRegisterAllComponents();if(Ribbons.IsEmpty()&&RibbonMesh&&TapeMaterial)Build();}
void AStationPoliceTape::BeginPlay(){Super::BeginPlay();ResetTape();}
void AStationPoliceTape::ResetTape(){BrokenStrands=0;TearSoundEvents=0;LastTearSoundTime=-1000;ContactSeconds=0;RibbonContacts=0;Accumulator=0;SimulationTime=0;Build();}
void AStationPoliceTape::Build()
{
 for(auto C:Ribbons)if(C)C->DestroyComponent();Ribbons.Empty();Strands.Empty();
 if(!RibbonMesh||!TapeMaterial)return;
 const int32 Count=bCrossing?3:1;
 for(int32 K=0;K<Count;++K)
 {
  FStrand S;S.A=LeftAnchor;S.B=RightAnchor;
  if(bCrossing){const float L[]={97,171,124},R[]={172,98,140};S.A.Z+=L[K];S.B.Z+=R[K];S.A.Y+=(K-1)*.8f;S.B.Y+=(K-1)*.8f;}
  for(int32 I=0;I<Segments+2;++I){const int32 J=I<=Seam?I:I-1;const float U=float(J)/Segments;S.P.Add(FMath::Lerp(S.A,S.B,U)-FVector(0,0,10*FMath::Sin(PI*U)));}
  S.Old=S.P;
  float Distance=0;
  for(int32 I=0;I<Segments+1;++I)
  {
   const float Length=(S.P[I+1]-S.P[I]).Size();S.Rest.Add(Length);
   if(I==Seam)continue;
   auto* C=NewObject<USplineMeshComponent>(this,NAME_None,RF_Transient);
   C->SetupAttachment(RootComponent);C->SetMobility(EComponentMobility::Movable);C->SetStaticMesh(RibbonMesh);C->SetForwardAxis(ESplineMeshAxis::X,false);
   C->SetCollisionEnabled(ECollisionEnabled::NoCollision);C->SetCastShadow(false);C->SetSplineUpDir(FVector::UpVector,false);
   C->SetStartScale(FVector2D(1,1),false);C->SetEndScale(FVector2D(1,1),false);
   C->RegisterComponent();Ribbons.Add(C);
   auto* M=UMaterialInstanceDynamic::Create(TapeMaterial,this);M->SetScalarParameterValue(TEXT("TileLength"),-Length/121.92f);M->SetScalarParameterValue(TEXT("TileOffset"),-Distance/121.92f);C->SetMaterial(0,M);Distance+=Length;
  }
  Strands.Add(MoveTemp(S));
 }
 DrawRibbon();
}
void AStationPoliceTape::Tick(float Dt)
{
 Super::Tick(Dt);if(Strands.IsEmpty())return;
 auto* Player=Cast<ACharacter>(UGameplayStatics::GetPlayerPawn(this,0));
 if(!Player)return;
 FVector Local=GetActorTransform().InverseTransformPosition(Player->GetActorLocation());
 // Broken state persists for this actor's play-session lifetime; distant tape sleeps.
 if(Local.SizeSquared()>FMath::Square(5000.f))return;
 const float Radius=Player->GetCapsuleComponent()->GetScaledCapsuleRadius();
 const float Half=Player->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
 const bool Moving=Player->GetVelocity().SizeSquared2D()>25;
 Accumulator=FMath::Min(Accumulator+Dt,.1f);
 while(Accumulator>=1.f/120){Step(1.f/120,Local,Radius,Half,true,Moving);Accumulator-=1.f/120;}
 DrawRibbon();
}
void AStationPoliceTape::Step(float Dt,const FVector& Player,float Radius,float Half,bool HasPlayer,bool Moving)
{
 SimulationTime+=Dt;
 TArray<bool> Touch;Touch.Init(false,Strands.Num());
 for(auto& S:Strands)
  for(int32 I=1;I<S.P.Num()-1;++I){FVector P=S.P[I];S.P[I]+=(P-S.Old[I])*.988f+FVector(0,40*FMath::Sin(SimulationTime*2+I*.3f),-980)*Dt*Dt;S.Old[I]=P;}
 for(int32 Iter=0;Iter<20;++Iter)
 {
  for(int32 K=0;K<Strands.Num();++K)
  {
   auto& S=Strands[K];
   for(int32 I=0;I<S.Rest.Num();++I)
   {
    if(I==Seam&&S.Broken)continue;
    FVector D=S.P[I+1]-S.P[I];float Len=D.Size();if(Len<.0001f)continue;
    float WA=I==0?0:1,WB=I+1==S.P.Num()-1?0:1;
    FVector C=D*((Len-S.Rest[I])/Len/(WA+WB));S.P[I]+=C*WA;S.P[I+1]-=C*WB;
   }
  }
  if(bCrossing)
   for(int32 A=0;A<Strands.Num();++A)for(int32 B=A+1;B<Strands.Num();++B)
    for(int32 I=1;I<Segments+1;++I)for(int32 J=1;J<Segments+1;++J)
    {
     auto& P=Strands[A].P[I];auto& Q=Strands[B].P[J];FVector D=P-Q;
     if(D.X*D.X+D.Z*D.Z<64&&FMath::Abs(D.Y)<.6f){float C=(.6f-FMath::Abs(D.Y))*.5f*(D.Y>0?1:-1);P.Y+=C;Q.Y-=C;if(Iter==0)++RibbonContacts;}
    }
  for(int32 K=0;K<Strands.Num();++K)
  {
   auto& S=Strands[K];
   for(int32 I=1;I<S.P.Num()-1;++I)
   {
    auto& P=S.P[I];
    if(bCrossing&&HasPlayer&&FMath::Abs(P.Z-Player.Z)<Half+3)
    {
     FVector2D D(P.X-Player.X,P.Y-Player.Y);float Len=D.Size();
     if(Len<Radius+2){D=Len>.01?D/Len:FVector2D(0,1);P.X=Player.X+D.X*(Radius+2);P.Y=Player.Y+D.Y*(Radius+2);Touch[K]=true;}
    }
    // Ground envelope follows anchor ground heights, preserving the main trail.
    float U=FMath::Clamp((P.X-LeftAnchor.X)/FMath::Max(1.f,RightAnchor.X-LeftAnchor.X),0.f,1.f);
    P.Z=FMath::Max(P.Z,FMath::Lerp(LeftAnchor.Z,RightAnchor.Z,U)+4-(bCrossing?0:150));
    if(bCrossing)
    {
     for(const FVector& Tree: {LeftAnchor-FVector(15,0,0),RightAnchor+FVector(15,0,0)})
     {
      FVector2D D(P.X-Tree.X,P.Y-Tree.Y);float R=D.Size();
      if(R<17&&R>.01){P.X=Tree.X+D.X*17/R;P.Y=Tree.Y+D.Y*17/R;}
     }
    }
   }
   S.P[0]=S.A;S.P.Last()=S.B;
  }
 }
 for(int32 K=0;K<Strands.Num();++K)
 {
  auto& S=Strands[K];
  if(Touch[K]&&Moving)S.ContactTime+=Dt;else S.ContactTime=FMath::Max(0.f,S.ContactTime-Dt*2);
  ContactSeconds=FMath::Max(ContactSeconds,S.ContactTime);
  // Contact must be sustained and physically load the seam; proximity cannot tear it.
  if(bCrossing&&!S.Broken&&S.ContactTime>.10f&&FMath::Abs(S.P[Seam].Y-S.A.Y)>PushDistance){
   S.Broken=true;++BrokenStrands;
   // One crisp burst for simultaneous strand failures; never play on mere proximity.
   if(TearSounds.Num()>0 && SimulationTime-LastTearSoundTime>.12f)
   {
    USoundBase* Sound=TearSounds[FMath::RandRange(0,TearSounds.Num()-1)];
    if(Sound)
    {
     UGameplayStatics::PlaySoundAtLocation(this,Sound,GetActorTransform().TransformPosition(S.P[Seam]),TearVolume,FMath::FRandRange(.97f,1.03f),0,TearAttenuation);
     LastTearSoundTime=SimulationTime;++TearSoundEvents;
    }
   }
  }
 }
}
void AStationPoliceTape::DrawRibbon()
{
 int32 Index=0;
 for(auto& S:Strands)for(int32 I=0;I<S.Rest.Num();++I)
 {
  if(I==Seam)continue;
   auto* C=Ribbons[Index++].Get();const FVector A=S.P[I],B=S.P[I+1],T=B-A;
  C->SetStartAndEnd(A,T,B,T,false);
  // Keep width perpendicular to the tangent as loose ends turn vertical.
  C->SetSplineUpDir(FMath::Abs(T.GetSafeNormal().Z)>.85f?FVector::ForwardVector:FVector::UpVector,false);
  C->SetStartRoll(.04f*FMath::Sin(I*.7f+SimulationTime),false);C->SetEndRoll(.04f*FMath::Sin((I+1)*.7f+SimulationTime),false);C->UpdateMesh();
 }
}
